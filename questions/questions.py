import nltk
import sys
import os
import string
import numpy

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    dictionary_corpus = {} 
    directory_path = str(directory) + os.sep 
    for files in os.scandir(directory_path):
        if files.path.endswith(".txt"):
            with open(files.path) as f:
                lines = f.read()
                dictionary_corpus[files.name] = lines
                

    return dictionary_corpus


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    
    word_list = nltk.word_tokenize(document)
    word_list = [word.lower() for word in word_list]
    for word in word_list:
        if word.isalpha():
            continue
        elif word in nltk.corpus.stopwords.words("english"):
            word_list.remove(word)
        elif word in string.punctuation:
            word_list.remove(word)
    return word_list

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    list_docs = list(documents.keys())
    num_docs = len(list_docs)
    word_idfs = {}
    for doc in documents:
        unique_list = []
        text = documents[doc]
        #getting list of unique words in the document to make sure we are not counting words that appear multiple
        # times more than once. Since we only need to count if it appeared in the document.
        for word in text:
            if word not in unique_list:
                unique_list.append(word)
        #counting with the unique list to make sure each word counted only once and added to the dict.
        for word in unique_list:
            word_idfs[word] = word_idfs.get(word, 0) + 1
             
    #Now calculate the actual IDF by taking the natural log of number of documents divided by the number of documents
    # the word showed up in. 
    for key_word in word_idfs:
        word_idfs[key_word] = numpy.log(num_docs/word_idfs.get(key_word)) 

    return word_idfs

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    n_files = {}
    for the_file in files:
        query_tf_idfs = []
        word_selection = files[the_file]
        for word in query:
            counter = 0
            for words in word_selection:
                if word == words:
                    counter += 1
            
            query_tf_idfs.append(idfs[word] * counter)
        
        n_files[the_file] = sum(query_tf_idfs)

    #returning in reverse order so top results are the first in the list.
    n_sorted = sorted(n_files.items(), key= lambda x: x[1], reverse = True)

    #keeping only the filenames information.
    return_list = [i[0] for i in n_sorted] 

    return return_list[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    n_sent = {}
    for sentence in sentences:
        words_sent = sentences[sentence]
        query_idfs = []
        seen_words = []
        counter = 0
        for word in query:
            for words in words_sent:
                if word in seen_words:
                    continue
                if word == words:
                    query_idfs.append(idfs[word])
                    seen_words.append(word)
                    counter += 1

        n_sent[sentence] = [sum(query_idfs), counter/len(words_sent)]

    #returning in reverse order so top results are the first in the list.
    n_sorted_sent = sorted(n_sent.items(), key = lambda x: (x[1][0],x[1][1]), reverse = True) 
    #keeping only the sentences information.
    return_list = [i[0] for i in n_sorted_sent]
    
    return return_list[:n]


if __name__ == "__main__":
    main()
