#!/bin/sh

if [ -z "$1" ]; then
	echo "Usage: hw3_parser.sh <grammar_filename> <test_sentence_filename> <output_filename>"
else
	/opt/python-3.6/bin/python3 CKY_parser.py $1 $2 $3
fi
