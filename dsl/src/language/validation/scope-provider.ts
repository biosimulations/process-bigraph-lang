import {DefaultScopeProvider, EMPTY_SCOPE, ReferenceInfo, Scope} from 'langium';
import {
    MemberCall,
    NamedElement,
    TypeRef,
    isMemberCall,
    isSimpleTypeRef,
    isStructType,
    isTupleType,
    isTypeAlias,
} from '../generated/ast.js';

/**
 * Scopes the members of a dotted reference (`a.b.c`): each segment after the first
 * resolves against the fields of the previous segment's struct type, or the named
 * elements of its tuple type.
 */
export class MyScopeProvider extends DefaultScopeProvider {
    override getScope(context: ReferenceInfo): Scope {
        if (context.property === 'element' && isMemberCall(context.container)) {
            const previous = context.container.previous;
            if (!previous) {
                return super.getScope(context);
            }
            const members = getMembers(inferType(previous));
            return members ? this.createScopeForNodes(members) : EMPTY_SCOPE;
        }
        return super.getScope(context);
    }
}

/**
 * Returns the declared type of the element a member chain refers to, or undefined if
 * any segment is unresolved or not a member of the previous segment's type.
 */
export function inferType(memberCall: MemberCall): TypeRef | undefined {
    const element = memberCall.element?.ref;
    if (!element) return undefined;
    if (memberCall.previous) {
        const members = getMembers(inferType(memberCall.previous));
        if (!members?.includes(element)) return undefined;
    }
    return element.type;
}

/**
 * Returns the named members of a struct or tuple type (following type aliases),
 * or undefined for types without members.
 */
function getMembers(typeRef: TypeRef | undefined): NamedElement[] | undefined {
    const seen = new Set<TypeRef>();
    while (typeRef && !seen.has(typeRef)) {
        seen.add(typeRef);
        if (isTupleType(typeRef)) {
            return typeRef.elements;
        }
        if (!isSimpleTypeRef(typeRef)) {
            return undefined;
        }
        const def = typeRef.type?.ref;
        if (isStructType(def)) {
            return def.fields;
        }
        if (!isTypeAlias(def)) {
            return undefined;
        }
        typeRef = def.type;
    }
    return undefined;
}
