// src/validation/TypeValidator.ts

import { ValidationAcceptor } from "langium";
import {
  CallableSignature,
  CallExpression,
  ConnectDecl,
  Field,
  InitDecl,
  isTupleType,
  ParamDecl,
  RemoteDef,
  StoreDecl,
  TypeRef,
  VarDef,
} from "../generated/ast.js";
import {
  isTypeAssignable,
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

  validateSignature(signature: CallableSignature, accept: ValidationAcceptor) {
    const seenParams = new Set<string>();
    for (const param of signature.params) {
      this.validateParam(param, accept, seenParams);
    }

    const seenResults = new Set<string>();
    for (const result of signature.results) {
      this.validateParam(result, accept, seenResults);
    }
  }

  private validateParam(
    param: ParamDecl,
    accept: ValidationAcceptor,
    seen: Set<string>,
  ) {
    if (seen.has(param.name)) {
      accept("error", `Duplicate parameter name '${param.name}'`, {
        node: param,
        property: "name",
      });
    } else {
      seen.add(param.name);
    }

    const resolvedType = resolveType(param.type);
    if (!resolvedType) {
      accept("error", `Could not resolve type`, { node: param.type });
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

  validateCallExpression(
    call: CallExpression,
    accept: ValidationAcceptor,
  ): void {
    const sig = call.callee?.ref?.signature;
    if (!sig) return;

    const paramMap = new Map(
      sig.params.map((p) => [p.name, resolveType(p.type)]),
    );
    const seen = new Set<string>();

    for (const arg of call.args) {
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
        accept("error", `Missing required argument '${name}'`, { node: call });
      }
    }
  }

  validateRemoteDef(remote: RemoteDef, accept: ValidationAcceptor) {
    if (
      remote.pythonPath &&
      !/^[a-zA-Z_][\w]*(\.[a-zA-Z_][\w]*)*$/.test(remote.pythonPath)
    ) {
      accept(
        "error",
        `Invalid Python path '${remote.pythonPath}'. Expected dot-separated identifiers.`,
        {
          node: remote,
          property: "pythonPath",
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

  checkConnectDecl(connect: ConnectDecl, accept: ValidationAcceptor): void {
    const remote = connect.callee?.ref as RemoteDef | undefined;
    if (!remote) {
      accept("error", `Unknown remote in connect`, { node: connect });
      return;
    }
    const sig = remote.signature;
    if (!sig) {
      accept("error", `Remote '${remote.name}' has no signature`, {
        node: connect,
      });
      return;
    }

    // Validate input arguments
    for (const arg of connect.args) {
      const param = sig.params.find((p) => p.name === arg.name);
      const store = arg.value?.store?.ref;
      if (!param) {
        accept("error", `Unknown parameter '${arg.name}' in remote`, {
          node: arg,
        });
        continue;
      }
      if (!store) {
        accept("error", `Unknown store for argument '${arg.name}'`, {
          node: arg.value,
        });
        continue;
      }
      if (!store.type) {
        accept("error", `Store '${store.name}' has no type`, {
          node: arg.value,
        });
        continue;
      }
      const paramType = resolveType(param.type);
      const storeType = resolveType(store.type);
      if (!isTypeAssignable(storeType, paramType)) {
        accept(
          "error",
          `Type mismatch: store '${store.name}' is not assignable to parameter '${param.name}'`,
          { node: arg.value },
        );
      }
    }

    // Validate output stores
    for (let i = 0; i < connect.outputs.length; i++) {
      const outputRef = connect.outputs[i];
      const store = outputRef.store?.ref;
      const result = sig.results[i];
      if (!result) {
        accept("error", `Too many output stores for remote '${remote.name}'`, {
          node: outputRef,
        });
        continue;
      }
      if (!store) {
        accept("error", `Unknown output store`, { node: outputRef });
        continue;
      }
      if (!store.type) {
        accept("error", `Store '${store.name}' has no type`, {
          node: outputRef,
        });
        continue;
      }
      const resultType = resolveType(result.type);
      const storeType = resolveType(store.type);
      if (!isTypeAssignable(resultType, storeType)) {
        accept(
          "error",
          `Type mismatch: remote result '${result.name}' is not assignable to store '${store.name}'`,
          { node: outputRef },
        );
      }
    }

    // Check for missing outputs
    if (connect.outputs.length < sig.results.length) {
      accept("error", `Missing output store(s) for remote '${remote.name}'`, {
        node: connect,
      });
    }
  }
}
