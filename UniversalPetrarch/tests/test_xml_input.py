import sys
sys.path.append('..')
import datetime
from bson.objectid import ObjectId
import petrarch_ud
import PETRreader


def test_petr_xml():
    petr_ud_results = petrarch_ud.run(["english_sample.xml"],
                                      "output.txt", True)
    print(petr_ud_results)
    #assert petr_ud_results == correct1_results

if __name__ == "__main__":
    test_petr_xml()
