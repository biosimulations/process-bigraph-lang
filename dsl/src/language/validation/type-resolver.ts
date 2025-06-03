// TypeResolver.ts
import {
  isArrayType,
  isMapType,
  isTupleType,
  isPrimitiveType,
  isSimpleTypeRef,
  isStructType,
  isTypeAlias,
  isVarRef,
  StructType,
  TypeRef,
  Value,
  isStructLiteral,
  isArrayLiteral,
  isMapLiteral,
  isIntLiteral,
  isFloatLiteral,
  isStringLiteral,
  isBoolLiteral,
  isTupleLiteral,
  CallExpression,
  CallableSignature,
  isCallExpression,
} from "../generated/ast.js";
import { ValidationAcceptor } from "langium";

// ============================
// Type Resolver
// ============================

export type ResolvedType =
  | { kind: "primitive"; name: string }
  | { kind: "struct"; type: StructType }
  | { kind: "alias"; target: ResolvedType }
  | { kind: "array"; elementType: ResolvedType }
  | { kind: "tuple"; elements: { name: string; type: ResolvedType }[] }
  | { kind: "map"; keyType: ResolvedType; valueType: ResolvedType };

export function resolveType(typeRef: TypeRef): ResolvedType {
  if (isSimpleTypeRef(typeRef)) {
    const def = typeRef.type?.ref;
    if (!def) throw new Error("Unresolved type reference");

    if (isTypeAlias(def)) {
      return {
        kind: "alias",
        target: resolveType(def.type),
      };
    }
    if (isPrimitiveType(def)) {
      return {
        kind: "primitive",
        name: def.name,
      };
    }
    if (isStructType(def)) {
      return {
        kind: "struct",
        type: def,
      };
    }
    throw new Error(`Unsupported TypeDef kind: ${def}`);
  } else if (isArrayType(typeRef)) {
    return {
      kind: "array",
      elementType: resolveType(typeRef.elementType),
    };
  } else if (isMapType(typeRef)) {
    return {
      kind: "map",
      keyType: resolveType(typeRef.keyType),
      valueType: resolveType(typeRef.valueType),
    };
  } else if (isTupleType(typeRef)) {
    const elements = [];
    for (const param of typeRef.elements) {
      const resolved = resolveType(param.type);
      elements.push({ name: param.name, type: resolved });
    }
    return { kind: "tuple", elements };
  }
  throw new Error("Unsupported TypeRef");
}

// ============================
// Type Validator
// ============================

export function validateValueAgainstType(
  value: Value,
  expected: ResolvedType,
  accept: ValidationAcceptor,
): boolean {
  // Handle VarRef: resolve and check its type
  if (isVarRef(value)) {
    const ref = value.ref;
    if (!ref || !ref.ref?.type) {
      accept("error", "Unresolved or untyped variable reference", {
        node: value,
      });
      return false;
    }
    const actualType = resolveType(ref.ref?.type);
    if (!isTypeAssignable(actualType, expected)) {
      accept(
        "error",
        `Variable reference is not assignable to expected type: actual=${typeToString(
          actualType,
        )}, expected=${typeToString(expected)}`,
        { node: value },
      );
      return false;
    }
    return true;
  }

  switch (expected.kind) {
    case "primitive":
      if (expected.name === "int") {
        if (!isIntLiteral(value)) {
          accept("error", `Expected value of type 'int'`, { node: value });
          return false;
        }
        return true;
      }
      if (expected.name === "float") {
        if (!(isFloatLiteral(value) || isIntLiteral(value))) {
          accept("error", `Expected value of type 'float' or 'int'`, {
            node: value,
          });
          return false;
        }
        return true;
      }
      if (expected.name === "string") {
        if (!isStringLiteral(value)) {
          accept("error", `Expected value of type 'string'`, { node: value });
          return false;
        }
        return true;
      }
      if (expected.name === "bool") {
        if (!isBoolLiteral(value)) {
          accept("error", `Expected value of type 'bool'`, { node: value });
          return false;
        }
        return true;
      }
      accept("error", `Unknown primitive type '${expected.name}'`, {
        node: value,
      });
      return false;
    case "struct":
      if (!isStructLiteral(value)) {
        accept("error", `Expected struct of type '${expected.type.name}'`, {
          node: value,
        });
        return false;
      }
      const definedFields = new Map(
        expected.type.fields.map((f) => [f.name, f]),
      );
      const seenFields = new Set<string>();
      let structValid = true;

      for (const f of value.fields) {
        const def = definedFields.get(f.name);
        if (!def) {
          accept(
            "error",
            `Field '${f.name}' is not valid for struct '${expected.type.name}'`,
            { node: f, property: "name" },
          );
          structValid = false;
          continue;
        }

        seenFields.add(f.name);
        const resolved = resolveType(def.type);
        if (!validateValueAgainstType(f.value, resolved, accept)) {
          structValid = false;
        }
      }

      for (const fieldName of definedFields.keys()) {
        if (!seenFields.has(fieldName)) {
          accept("error", `Missing field '${fieldName}' in struct literal`, {
            node: value,
          });
          structValid = false;
        }
      }
      return structValid;

    case "array":
      if (!isArrayLiteral(value)) {
        accept("error", `Expected an array literal`, { node: value });
        return false;
      }

      let arrayValid = true;
      for (const [index, e] of value.elements.entries()) {
        if (!validateValueAgainstType(e, expected.elementType, accept)) {
          accept("error", `Invalid element at index ${index}`, { node: e });
          arrayValid = false;
        }
      }
      return arrayValid;

    case "tuple":
      if (isCallExpression(value)) {
        const sig = value.callee?.ref?.signature;
        if (!sig) return false;

        const resultMap = new Map(
          sig.results.map((p) => [p.name, resolveType(p.type)]),
        );
        const expectedMap = new Map(
          expected.elements.map((p) => [p.name, p.type]),
        );
        let valid = true;

        for (const [name, type] of expectedMap) {
          const actualType = resultMap.get(name);
          if (!actualType || !isTypeAssignable(actualType, type)) {
            accept(
              "error",
              `Call result '${name}' is not compatible with expected type`,
              { node: value },
            );
            valid = false;
          }
        }
        return valid;
      }

      if (!isTupleLiteral(value)) {
        accept("error", `Expected a tuple literal`, { node: value });
        return false;
      }

      let hasError = false;
      const expectedFields = new Map(
        expected.elements.map((e) => [e.name, e.type]),
      );
      const seen = new Set<string>();

      for (const field of value.fields) {
        const name = field.name;
        if (seen.has(name)) {
          accept("error", `Duplicate tuple field '${name}'`, {
            node: field,
            property: "name",
          });
          hasError = true;
          continue;
        }
        seen.add(name);

        const expectedType = expectedFields.get(name);
        if (!expectedType) {
          accept("error", `Field '${name}' is not valid for this tuple`, {
            node: field,
            property: "name",
          });
          hasError = true;
          continue;
        }

        if (!validateValueAgainstType(field.value, expectedType, accept)) {
          hasError = true;
        }
      }

      for (const [name] of expectedFields) {
        if (!seen.has(name)) {
          accept("error", `Missing tuple field '${name}'`, { node: value });
          hasError = true;
        }
      }

      return !hasError;

    case "map":
      if (!isMapLiteral(value)) {
        accept("error", `Expected a map literal`, { node: value });
        return false;
      }

      let mapValid = true;
      for (const entry of value.entries) {
        const keyValid = validateValueAgainstType(
          entry.key,
          expected.keyType,
          accept,
        );
        const valValid = validateValueAgainstType(
          entry.value,
          expected.valueType,
          accept,
        );
        if (!keyValid || !valValid) {
          mapValid = false;
        }
      }
      return mapValid;

    case "alias":
      return validateValueAgainstType(value, expected.target, accept);
  }
}

export function resolveCallExpr(
  call: CallExpression,
): CallableSignature | undefined {
  return call.callee?.ref?.signature;
}

export function isTypeAssignable(
  actual: ResolvedType,
  expected: ResolvedType,
): boolean {
  // Unwrap aliases
  while (actual.kind === "alias") actual = actual.target;
  while (expected.kind === "alias") expected = expected.target;

  if (actual.kind === "primitive" && expected.kind === "primitive") {
    if (actual.name === expected.name) return true;
    if (actual.name === "int" && expected.name === "float") return true;
    return false;
  }

  if (actual.kind === "struct" && expected.kind === "struct") {
    if (actual.type.name !== expected.type.name) return false;
    // For strict matching; for subtyping, you'd need deeper checking
    return true;
  }

  if (actual.kind === "array" && expected.kind === "array") {
    return isTypeAssignable(actual.elementType, expected.elementType);
  }

  if (actual.kind === "map" && expected.kind === "map") {
    return (
      isTypeAssignable(actual.keyType, expected.keyType) &&
      isTypeAssignable(actual.valueType, expected.valueType)
    );
  }

  if (actual.kind === "tuple" && expected.kind === "tuple") {
    const actualFields = new Map(actual.elements.map((e) => [e.name, e.type]));
    for (const e of expected.elements) {
      const actualField = actualFields.get(e.name);
      if (!actualField || !isTypeAssignable(actualField, e.type)) return false;
    }
    return true;
  }

  return false;
}

function typeToString(type: ResolvedType): string {
  switch (type.kind) {
    case "primitive":
      return type.name;
    case "struct":
      return `struct ${type.type.name}`;
    case "array":
      return `array<${typeToString(type.elementType)}>`;
    case "map":
      return `map<${typeToString(type.keyType)}, ${typeToString(
        type.valueType,
      )}>`;
    case "tuple":
      return `tuple(${type.elements
        .map((e) => `${e.name}: ${typeToString(e.type)}`)
        .join(", ")})`;
    case "alias":
      return typeToString(type.target);
    default:
      return "unknown";
  }
}
