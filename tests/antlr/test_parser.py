from pathlib import Path

from antlr4 import FileStream, CommonTokenStream  # type: ignore[import-untyped]
from process_bigraph_lang.antlr.pblangLexer import pblangLexer
from process_bigraph_lang.antlr.pblangParser import pblangParser


def test_parse_abc(model_path_abc: Path) -> None:
    input_stream = FileStream(fileName=str(model_path_abc))
    lexer = pblangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = pblangParser(stream)
    model = parser.model()

    units_strs: list[str] = [pretty_print(unit.toStringTree(recog=parser)) for unit in model.unit()]
    assert units_strs == [
        '(unit unit uM_per_h : [ "10e-6 mole/liter/h" ])',
        '(unit unit uM : [ "10e-6 mole/liter" ])',
        "(unit unit conc : uM_per_h)",
        '(unit unit hour : [ "h" ])',
        '(unit unit dimensionless : [ "1" ])',
    ]
    types_strs: list[str] = [pretty_print(typ.toStringTree(recog=parser)) for typ in model.typeDef()]
    assert types_strs == [
        "(typeDef type float default \n  (defaultValue 0.0))",
        "(typeDef type concentration extends float default \n  (defaultValue 1.0))",
    ]
    definition_strs: list[str] = [pretty_print(def_.toStringTree(recog=parser)) for def_ in model.definition()]
    assert definition_strs == [
        "(definition def exp \n  ( \n    (declaredParameter a) ) : builtin)",
        "(definition def my_update \n"
        "  ( \n"
        "    (declaredParameter substrate) , \n"
        "    (declaredParameter rate) , \n"
        "    (declaredParameter interval) ) : \n"
        "  (expression \n"
        "    (addition \n"
        "      (multiplication \n"
        "        (exponentiation \n"
        "          (modulo \n"
        "            (primaryExpression substrate)))) + \n"
        "      (multiplication \n"
        "        (exponentiation \n"
        "          (modulo \n"
        "            (primaryExpression rate))) * \n"
        "        (exponentiation \n"
        "          (modulo \n"
        "            (primaryExpression interval)))))) ;)",
    ]
    store_strs: list[str] = [pretty_print(def_.toStringTree(recog=parser)) for def_ in model.storeDef()]
    assert store_strs == [
        "(storeDef store_def medium state_def \n"
        "  (storeDefStateDef \n"
        "    (schemaItem glucose : float default \n"
        "      (defaultValue 3.0) [ uM ])) state_def \n"
        "  (storeDefStateDef \n"
        "    (schemaItem calcium : float default \n"
        "      (defaultValue 0.5))))",
        "(storeDef store_def cell parent \n"
        "  (storeDefRef medium) state_def \n"
        "  (storeDefStateDef \n"
        "    (schemaItem glucose : float default \n"
        "      (defaultValue 0.0))) state_def \n"
        "  (storeDefStateDef \n"
        "    (schemaItem calcium : float default \n"
        "      (defaultValue 0.0))))",
        "(storeDef store_def nucleus parent \n"
        "  (storeDefRef cell) state_def \n"
        "  (storeDefStateDef \n"
        "    (schemaItem glucose : float default \n"
        "      (defaultValue 0.0))) state_def \n"
        "  (storeDefStateDef \n"
        "    (schemaItem calcium : float default \n"
        "      (defaultValue 0.0))))",
    ]
    processDef_strs: list[str] = [pretty_print(def_.toStringTree(recog=parser)) for def_ in model.processDef()]
    assert processDef_strs == [
        "(processDef process_def MyProcess \n"
        "  (pythonPath path my_processes . Process1) \n"
        "  (processParameter param \n"
        "    (schemaItem calcium_growth : float default \n"
        "      (defaultValue 0.1) [ uM_per_h ])) \n"
        "  (processParameter param \n"
        "    (schemaItem glucose_growth : float default \n"
        "      (defaultValue 0.1) [ uM_per_h ])) \n"
        "  (processParameter param \n"
        "    (schemaItem dt : float default \n"
        "      (defaultValue 0.1) [ hour ])) \n"
        "  (processParameter param \n"
        "    (schemaItem alpha : float default \n"
        "      (defaultValue 0.1) [ dimensionless ])) \n"
        "  (processVariable var \n"
        "    (schemaItem glucose : float)) \n"
        "  (processVariable var \n"
        "    (schemaItem calcium : float [ conc ])) inputs \n"
        "  (processInput glucose) \n"
        "  (processInput calcium) outputs \n"
        "  (processOutput glucose) \n"
        "  (processOutput calcium) updates \n"
        "  (update glucose := \n"
        "    (expression \n"
        "      (addition \n"
        "        (multiplication \n"
        "          (exponentiation \n"
        "            (modulo \n"
        "              (primaryExpression my_update \n"
        "                ( \n"
        "                  (expression \n"
        "                    (addition \n"
        "                      (multiplication \n"
        "                        (exponentiation \n"
        "                          (modulo \n"
        "                            (primaryExpression glucose)))))) , \n"
        "                  (expression \n"
        "                    (addition \n"
        "                      (multiplication \n"
        "                        (exponentiation \n"
        "                          (modulo \n"
        "                            (primaryExpression glucose_growth)))))) , \n"
        "                  (expression \n"
        "                    (addition \n"
        "                      (multiplication \n"
        "                        (exponentiation \n"
        "                          (modulo \n"
        "                            (primaryExpression dt)))))) ))))))) ;) \n"
        "  (update calcium := \n"
        "    (expression \n"
        "      (addition \n"
        "        (multiplication \n"
        "          (exponentiation \n"
        "            (modulo \n"
        "              (primaryExpression calcium))) * \n"
        "          (exponentiation \n"
        "            (modulo \n"
        "              (primaryExpression \n"
        "                ( \n"
        "                  (expression \n"
        "                    (addition \n"
        "                      (multiplication \n"
        "                        (exponentiation \n"
        "                          (modulo \n"
        "                            (primaryExpression 1)))) - \n"
        "                      (multiplication \n"
        "                        (exponentiation \n"
        "                          (modulo \n"
        "                            (primaryExpression exp \n"
        "                              ( \n"
        "                                (expression \n"
        "                                  (addition \n"
        "                                    (multiplication \n"
        "                                      (exponentiation \n"
        "                                        (modulo \n"
        "                                          (primaryExpression dt)))))) "
        "))))))) ))))) + \n"
        "        (multiplication \n"
        "          (exponentiation \n"
        "            (modulo \n"
        "              (primaryExpression alpha))) * \n"
        "          (exponentiation \n"
        "            (modulo \n"
        "              (primaryExpression calcium_growth))) * \n"
        "          (exponentiation \n"
        "            (modulo \n"
        "              (primaryExpression dt)))))) ;))"
    ]


def pretty_print(input_str: str) -> str:
    indent = 0
    result = []
    for char in input_str:
        if char == "(":
            result.append("\n" + "  " * indent + char)
            indent += 1
        elif char == ")":
            indent -= 1
            result.append(char)
        elif char == " " and result and result[-1].endswith("\n"):
            # Skip extra spaces after a newline
            continue
        else:
            result.append(char)
    return "".join(result).strip()
