// src/validation/TypeValidator.ts

import { ValidationAcceptor } from "langium";
import {
  Binding,
  CallableLiteral,
  ConnectStatement,
  Field,
  InitDecl,
  isTupleType,
  ParamDecl,
  RemoteCallableType,
  StoreDecl,
  TypeRef,
  VarDef,
} from "../generated/ast.js";
import {
  isTypeAssignable,
  ResolvedType,
  resolveType,
  typeToString,
  validateValueAgainstType,
} from "./type-resolver.js";
import { inferType } from "./scope-provider.js";

export class TypeValidator {
  checkVarDef(varDef: VarDef, accept: ValidationAcceptor): void {
    if (varDef.type && varDef.value) {
      try {
        const resolvedType = resolveType(varDef.type);
        validateValueAgainstType(varDef.value, resolvedType, accept);
      } catch (err) {
        accept("error", `Type resolution error: ${(err as Error).message}`, {
          node: varDef.type,
        });
      }
    }
  }
  checkField(field: Field, accept: ValidationAcceptor): void {
    if (field.type && field.default) {
      try {
        const resolved = resolveType(field.type);
        const valid = validateValueAgainstType(field.default, resolved, accept);
        if (!valid) {
          accept("error", `Default value does not match field type`, {
            node: field.default,
          });
        }
      } catch (err) {
        accept("error", `Type resolution error: ${(err as Error).message}`, {
          node: field.type,
        });
      }
    }
  }

  validateTypeRef(typeRef: TypeRef, accept: ValidationAcceptor) {
    if (isTupleType(typeRef)) {
      const seen = new Set<string>();
      for (const param of typeRef.elements) {
        if (seen.has(param.name)) {
          accept("error", `Duplicate tuple field name '${param.name}'`, {
            node: param,
            property: "name",
          });
        } else {
          seen.add(param.name);
        }

        const resolved = resolveType(param.type);
        if (!resolved) {
          accept("error", `Could not resolve tuple field type`, {
            node: param.type,
          });
        }
      }
    } else {
      const resolved = resolveType(typeRef);
      if (!resolved) {
        accept("error", `Unknown or invalid type`, {
          node: typeRef,
        });
      }
    }
  }

  validateCallableLiteral(
    callable_literal: CallableLiteral,
    accept: ValidationAcceptor,
  ): void {
    const config = callable_literal.callable_type?.ref?.config;
    if (!config) return;

    const paramMap = new Map(
      config.elements.map((p) => [p.name, resolveType(p.type)]),
    );
    const seen = new Set<string>();

    for (const arg of callable_literal.configArgs) {
      const name = arg.name;
      if (seen.has(name)) {
        accept("error", `Duplicate argument '${name}'`, {
          node: arg,
          property: "name",
        });
        continue;
      }
      seen.add(name);
      const expected = paramMap.get(name);
      if (!expected) {
        accept("error", `Unexpected argument '${name}'`, {
          node: arg,
          property: "name",
        });
        continue;
      }
      validateValueAgainstType(arg.value, expected, accept);
    }

    for (const [name] of paramMap) {
      if (!seen.has(name)) {
        accept("error", `Missing required argument '${name}'`, { node: callable_literal });
      }
    }
  }

  validateRemoteCallableType(remote: RemoteCallableType, accept: ValidationAcceptor) {
    if (
      remote.address &&
      !/^[a-zA-Z_][\w]*(\.[a-zA-Z_][\w]*)*$/.test(remote.address)
    ) {
      accept(
        "error",
        `Invalid Python path '${remote.address}'. Expected dot-separated identifiers.`,
        {
          node: remote,
          property: "address",
        },
      );
    }
  }

  checkStoreDecl(store: StoreDecl, accept: ValidationAcceptor): void {
    if (!store.type) {
      accept("error", `Store '${store.name}' must have a type`, {
        node: store,
      });
      return;
    }
    try {
      const resolved = resolveType(store.type);
      if (!resolved) {
        accept("error", `Unknown type for store '${store.name}'`, {
          node: store.type,
        });
      }
    } catch (err) {
      accept("error", `Type resolution error: ${(err as Error).message}`, {
        node: store.type,
      });
    }
  }

  checkInitDecl(init: InitDecl, accept: ValidationAcceptor): void {
    const store = init.store?.ref;
    if (!store) {
      accept("error", `Unknown store in init`, { node: init });
      return;
    }
    if (!store.type) {
      accept("error", `Store '${store.name}' has no type`, { node: init });
      return;
    }
    try {
      const storeType = resolveType(store.type);
      if (!validateValueAgainstType(init.value, storeType, accept)) {
        accept("error", `Init value does not match store type`, {
          node: init.value,
        });
      }
    } catch (err) {
      accept("error", `Type resolution error: ${(err as Error).message}`, {
        node: store.type,
      });
    }
  }

  validateConnectStatement(
    connect: ConnectStatement,
    accept: ValidationAcceptor,
  ): void {
    const instance = connect.instance?.ref?.ref;
    if (!instance) return; // unresolved instance is reported by the linker

    let instanceType: ResolvedType;
    try {
      instanceType = resolveType(instance.type);
    } catch (err) {
      accept("error", `Type resolution error: ${(err as Error).message}`, {
        node: connect.instance,
      });
      return;
    }
    while (instanceType.kind === "alias") instanceType = instanceType.target;
    if (instanceType.kind !== "remoteCallable") {
      accept(
        "error",
        `'${instance.name}' is not a remote step or process instance (type ${typeToString(instanceType)})`,
        { node: connect.instance },
      );
      return;
    }
    const remote = instanceType.type;

    // inputs flow from the bound element into the remote's parameter
    this.checkBindings(
      connect.inputBindings,
      remote.inputs?.elements ?? [],
      "input",
      remote.name,
      (bound, port) => isTypeAssignable(bound, port),
      accept,
    );
    // outputs flow from the remote's result into the bound element
    this.checkBindings(
      connect.outputBindings,
      remote.outputs?.elements ?? [],
      "output",
      remote.name,
      (bound, port) => isTypeAssignable(port, bound),
      accept,
    );

    const missing = (ports: ParamDecl[] | undefined, bindings: Binding[]) =>
      (ports ?? [])
        .map((p) => p.name)
        .filter((name) => !bindings.some((b) => b.name === name));
    for (const name of missing(remote.inputs?.elements, connect.inputBindings)) {
      accept("error", `Missing input binding '${name}' for '${remote.name}'`, {
        node: connect,
        property: "inputBindings",
      });
    }
    for (const name of missing(remote.outputs?.elements, connect.outputBindings)) {
      accept("error", `Missing output binding '${name}' for '${remote.name}'`, {
        node: connect,
        property: "outputBindings",
      });
    }
  }

  private checkBindings(
    bindings: Binding[],
    ports: ParamDecl[],
    direction: "input" | "output",
    remoteName: string,
    isCompatible: (bound: ResolvedType, port: ResolvedType) => boolean,
    accept: ValidationAcceptor,
  ): void {
    const seen = new Set<string>();
    for (const binding of bindings) {
      if (seen.has(binding.name)) {
        accept("error", `Duplicate ${direction} binding '${binding.name}'`, {
          node: binding,
          property: "name",
        });
        continue;
      }
      seen.add(binding.name);

      const port = ports.find((p) => p.name === binding.name);
      if (!port) {
        accept(
          "error",
          `'${remoteName}' has no ${direction} named '${binding.name}'`,
          { node: binding, property: "name" },
        );
        continue;
      }

      const boundTypeRef = inferType(binding.variable);
      if (!boundTypeRef) continue; // unresolved reference is reported by the linker
      try {
        const boundType = resolveType(boundTypeRef);
        const portType = resolveType(port.type);
        if (!isCompatible(boundType, portType)) {
          accept(
            "error",
            `Type mismatch for ${direction} '${binding.name}': bound element has type ${typeToString(boundType)}, '${remoteName}' ${direction} has type ${typeToString(portType)}`,
            { node: binding, property: "variable" },
          );
        }
      } catch (err) {
        accept("error", `Type resolution error: ${(err as Error).message}`, {
          node: binding,
          property: "variable",
        });
      }
    }
  }
}
