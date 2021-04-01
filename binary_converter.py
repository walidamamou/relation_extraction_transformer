import json
import typer
from pathlib import Path
from spacy.tokens import Span, DocBin, Doc
from spacy.vocab import Vocab
from wasabi import Printer
from spacy.tokenizer import Tokenizer
from spacy.lang.en import English
import spacy
nlp = spacy.blank("en")
# Create a blank Tokenizer with just the English vocab
msg = Printer()
MAP_LABELS = {
    "DEGREE_IN": "DEGREE_IN",
    "EXPERIENCE_IN": "EXPERIENCE_IN",
}
# path to the annotation data
path="path_to/relation.txt"
def main(json_loc: Path, train_file: Path, dev_file: Path,test_file:Path):
    """Creating the corpus from UBIAI annotations."""
    Doc.set_extension("rel", default={},force=True)
    vocab = Vocab()
    docs = {"train": [], "dev": [], "test": [], "total": []}
    ids = {"train": set(), "dev": set(), "test":set()}
    count_all = {"train": 0, "dev": 0, "test": 0,"total": 0}
    count_pos = {"train": 0, "dev": 0, "test": 0,"total": 0}
with open(json_loc) as jsonfile:
        file = json.load(jsonfile)
        for example in file:
            span_starts = set()
            neg = 0
            pos = 0
            # Parse the tokens
            tokens=nlp(example["document"])
            spaces=[]
            spaces = [True if tok.whitespace_ else False for tok in          tokens]
            words = [t.text for t in tokens]
            doc = Doc(nlp.vocab, words=words, spaces=spaces)
# Parse the SKILLS, EXPERIENCE, DIPLOMA and DIPLOMA_MAJOR entities
            spans = example["tokens"]
            entities = []
            span_end_to_start = {}
            for span in spans:
                entity = doc.char_span(span["start"], span["end"], label=span["entityLabel")
span_end_to_start[span["token_start"]] = span["token_start"]
                #print(span_end_to_start)
                entities.append(entity)
                span_starts.add(span["token_start"])
doc.ents = entities
# Parse the relations
            rels = {}
            for x1 in span_starts:
                for x2 in span_starts:
                    rels[(x1, x2)] = {}
                    #print(rels)
            relations = example["relations"]
            #print(len(relations))
            for relation in relations:
                # the 'head' and 'child' annotations refer to the end token in the span
                # but we want the first token
                start = span_end_to_start[relation["head"]]
                end = span_end_to_start[relation["child"]]
                label = relation["relationLabel"]
                #print(rels[(start, end)])
                #print(label)
                #label = MAP_LABELS[label]
                if label not in rels[(start, end)]:
                    rels[(start, end)][label] = 1.0
                    pos += 1
                    #print(pos)
                    #print(rels[(start, end)])
# The annotation is complete, so fill in zero's where the data is missing
            for x1 in span_starts:
                for x2 in span_starts:
                    for label in MAP_LABELS.values():
                        if label not in rels[(x1, x2)]:
                            neg += 1
                            rels[(x1, x2)][label] = 0.0
#print(rels[(x1, x2)])
            doc._.rel = rels
            #print(doc._.rel)
# only keeping documents with at least 1 positive case
            if pos > 0:
                    docs["total"].append(doc)
                    count_pos["total"] += pos
                    count_all["total"] += pos + neg
#print(len(docs["total"]))
    docbin = DocBin(docs=docs["total"], store_user_data=True)
    docbin.to_disk(train_file)
    msg.info(
        f"{len(docs['total'])} training sentences"
    )
main(path, train_file, dev_file, test_file)