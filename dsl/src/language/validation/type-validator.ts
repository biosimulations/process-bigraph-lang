// src/validation/TypeValidator.ts

import { ValidationAcceptor } from "langium";
import {
  CallableLiteral,
  ConnectStatement,
  Field,
  InitDecl,
  // isRemoteCallableType,
  isTupleType,
  RemoteCallableType,
  StoreDecl,
  TypeRef,
  VarDef,
} from "../generated/ast.js";
import {
  resolveType,
  validateValueAgainstType,
} from "./type-resolver.js";

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

  validateConnectStatement(connect: ConnectStatement, accept: ValidationAcceptor): void {
    // const remoteRef = connect.instance;
    // if (!remoteRef) {
    //   accept("error", `Unknown remote in connect`, { node: connect.instance });
    //   return;
    // }
    // const remoteType = remoteRef.ref?.ref;
    // if (!remoteType) {
    //   accept("error", `Remote callable reference is missing`, { node: connect.instance });
    //   return;
    // }
    // const instanceType = resolveType(remoteType.type);
    //
    // if (!instanceType || !isRemoteCallableType(instanceType)) {
    //   accept("error", `Remote callable not found`, { node: connect.instance });
    //   return;
    // }
    //
    // const callableType = instanceType as RemoteCallableType;
    //
    // // Validate input arguments
    // for (const binding of connect.inputBindings) {
    //   const param = callableType.inputs?.elements.find((p) => p.name === binding.name);
    //   const store = binding.name.value?.store?.ref;
    //   if (!param) {
    //     accept("error", `Unknown parameter '${arg.name}' in remote`, {
    //       node: arg,
    //     });
    //     continue;
    //   }
    //   if (!store) {
    //     accept("error", `Unknown store for argument '${arg.name}'`, {
    //       node: arg.value,
    //     });
    //     continue;
    //   }
    //   if (!store.type) {
    //     accept("error", `Store '${store.name}' has no type`, {
    //       node: arg.value,
    //     });
    //     continue;
    //   }
    //   const paramType = resolveType(param.type);
    //   const storeType = resolveType(store.type);
    //   if (!isTypeAssignable(storeType, paramType)) {
    //     accept(
    //         "error",
    //         `Type mismatch: store '${store.name}' is not assignable to parameter '${param.name}'`,
    //         { node: arg.value },
    //     );
    //   }
    // }
    //
    // // TODO: Check for missing inputs
    // if (connect.outputs.length < sig.results.length) {
    //   accept("error", `Missing output store(s) for remote '${remote.name}'`, {
    //     node: connect,
    //   });
    // }
    //
    // // Validate output stores
    // for (const binding of connect.outputBindings) {
    //   if (binding === binding) {}  // This is a placeholder to avoid unused variable warning
    //   // TODO: Check if the binding matches a parameter in the remote callable's outputs tuple
    // }
    //
    // // TODO: Check for missing outputs
  }
}
