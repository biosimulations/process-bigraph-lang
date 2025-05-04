ANTLR_JAR = antlr-4.13.1-complete.jar
GRAMMAR = pblang.g4

all: gen-cpp gen-python

gen-cpp:
	java -jar $(ANTLR_JAR) -Dlanguage=Cpp -o ../cpp/src/antlr $(GRAMMAR)

gen-python:
	java -jar $(ANTLR_JAR) -Dlanguage=Python3 -o ../process_bigraph_lang/antlr $(GRAMMAR)

clean:
	rm -rf gen-cpp gen-python
