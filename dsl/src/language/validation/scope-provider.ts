import {DefaultScopeProvider, EMPTY_SCOPE, ReferenceInfo, Scope} from 'langium';
import { MemberCall, isVarDef, isField, isStoreDecl, isStructType, isMemberCall, isSimpleTypeRef } from '../generated/ast.js';

export class MyScopeProvider extends DefaultScopeProvider {
    override getScope(context: ReferenceInfo): Scope {
        if (context.property === 'element' && isMemberCall(context.container)) {
            const memberCall = context.container as MemberCall;
            const previous = memberCall.previous;
            if (!previous) {
                return super.getScope(context);
            }
            const previousType = inferType(previous); // Implement this for your type system
            if (isStructType(previousType)) { // Or your own type check
                return this.createScopeForNodes(previousType.fields);
            }
            return EMPTY_SCOPE;
        }
        return super.getScope(context);
    }
}

// export function inferType(memberCall: MemberCall): any {
//     // Traverse the chain to the root element
//     let current = memberCall;
//     while (current.previous) {
//         current = current.previous;
//     }
//     const element = current.element?.ref;
//     if (!element) return undefined;
//
//     // For VarDef, Field, StoreDecl, return their type
//     if (isVarDef(element) || isField(element) || isStoreDecl(element)) {
//         return element.type;
//     }
//     // Add more cases as needed
//     return undefined;
// }




export function inferType(memberCall: MemberCall): any {
    // Start with the first element in the chain
    let current: MemberCall | undefined = memberCall;
    let type: any = undefined;

    // Find the root element and get its type
    while (current?.previous) {
        current = current.previous;
    }
    const element = current?.element?.ref;
    if (!element) return undefined;

    if (isVarDef(element) || isField(element) || isStoreDecl(element)) {
        type = element.type;
    } else {
        return undefined;
    }

    // Walk the chain to resolve each member
    current = memberCall;
    const chain: MemberCall[] = [];
    while (current?.previous) {
        chain.unshift(current);
        current = current.previous;
    }

    for (const call of chain) {
        // Only structs have fields
        if (isSimpleTypeRef(type) && isStructType(type.type?.ref)) {
            const struct = type.type.ref;
            const field = struct.fields.find(f => f.name === call.element?.ref?.name);
            if (!field) return undefined;
            type = field.type;
        } else {
            return undefined;
        }
    }
    return type;
}