// src/validation/TypeValidator.ts

import { ValidationAcceptor } from 'langium';
import {CallableSignature, Field, isTupleType, ParamDecl, TypeRef, VarDef} from '../generated/ast.js';
import { resolveType, validateValueAgainstType } from './type-resolver.js';

export class TypeValidator {

    checkVarDef(varDef: VarDef, accept: ValidationAcceptor): void {
        if (varDef.type && varDef.value) {
            try {
                const resolvedType = resolveType(varDef.type);
                const isValid = validateValueAgainstType(varDef.value, resolvedType, accept);

                if (!isValid) {
                    accept('error', `Value does not match declared type`, {
                        node: varDef.value
                    });
                }
            } catch (err) {
                accept('error', `Type resolution error: ${(err as Error).message}`, {
                    node: varDef.type
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
                    accept('error', `Default value does not match field type`, { node: field.default });
                }
            } catch (err) {
                accept('error', `Type resolution error: ${(err as Error).message}`, { node: field.type });
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

    private validateParam(param: ParamDecl, accept: ValidationAcceptor, seen: Set<string>) {
        if (seen.has(param.name)) {
            accept('error', `Duplicate parameter name '${param.name}'`, { node: param, property: 'name' });
        } else {
            seen.add(param.name);
        }

        const resolvedType = resolveType(param.type);
        if (!resolvedType) {
            accept('error', `Could not resolve type`, { node: param.type });
        }
    }

    validateTypeRef(typeRef: TypeRef, accept: ValidationAcceptor) {
        if (isTupleType(typeRef)) {
            const seen = new Set<string>();
            for (const param of typeRef.elements) {
                if (seen.has(param.name)) {
                    accept('error', `Duplicate tuple field name '${param.name}'`, {
                        node: param,
                        property: 'name'
                    });
                } else {
                    seen.add(param.name);
                }

                const resolved = resolveType(param.type);
                if (!resolved) {
                    accept('error', `Could not resolve tuple field type`, {
                        node: param.type
                    });
                }
            }
        } else {
            const resolved = resolveType(typeRef);
            if (!resolved) {
                accept('error', `Unknown or invalid type`, {
                    node: typeRef
                });
            }
        }
    }

}
