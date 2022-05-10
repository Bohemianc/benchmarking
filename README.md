# Benchmarking

## Getting Requirements

+ For constructing benchmarks
    + python 3.7.0
    + requests_html: `pip install requests_html`
    + tensorflow 1.14.0
+ For query answering
    + java 1.8

## Constructing Benchmarks

1. Compiling `QuatE`
    ```sh
    cd QuatE-master
    bash make.sh
    cd ..
    mkdir release
    mv QuatE-master/release/Base.so release/
    ```
2. Learning rules
    ```sh
    python -u main.py
    ```
    + parameters
        + test_id: directory to store output files
        + RULE_LEN: rule length
        + RULE_DEP: rewriting depth
        + LIMIT_RULES: the maximum value of the number of rules of some target predicate when reading a file of rules
        + BEAM_SIZE: the maximum value of learned rules of some target predicate is `BEAM_SIZE//2`
        + others: depends the volume of data sampled for learning rules
3. Merging learned rules without recursion and sampling data according to the rules
    ```sh
    python -u sampling_qa.py
    ```
   > Remember to change the names of files or directories

## Benchmarks for Evaluations

+ queries
    + LC-QuAD (question collection of 5K natural language questions with their corresponding SPARQL
      queries): `queries/linked.json`
    + 1961 SPARQL queries after filtering: `queries/sparql1961.txt`
    + 5 SPARQL quesries used for evaluations in DLGP format: `queries/sparql1961-5.dlp`
+ ontologies for evaluations
    + `rules/rules_*.dlp` named by the number of rules in it
+ datasets for evaluations
    + [https://drive.google.com/drive/folders/1Bppxo1ns5fKBmH6cwYR2hK3Tp6LoJhum?usp=sharing](https://drive.google.com/drive/folders/1Bppxo1ns5fKBmH6cwYR2hK3Tp6LoJhum?usp=sharing)
    + `sampling_qa.py`: getting facts by rules and expected volume of them from the data pool above

## Tested Systems

+
Click [https://drive.google.com/drive/folders/1Y_p-5eaX4ZBAhq9zBBTn3bUVDHdBeeZV?usp=sharing](https://drive.google.com/drive/folders/1Y_p-5eaX4ZBAhq9zBBTn3bUVDHdBeeZV?usp=sharing)
for runnable jar files of Graal and Drewer
+ Graal
    + Run command
      ```sh
      java -Xms8g -Xmx8g -jar graal.jar -o [ontology_file] -q [query_file] -d [dataset_dir]
      ``` 
      > the ontology, queries and the dataset are all in DLGP format proposed by Graal
    + Click [https://graphik-team.github.io/graal/](https://graphik-team.github.io/graal/) for more details
+ Drewer
    + Run command
      ```sh
      java -Xms8g -Xmx8g -jar drewer.jar -o [ontology_file] -q [query_file] -d [dataset_dir]
      ``` 
      > the ontology and queries are both in DLGP format as Graal, while the dataset is in CSV format named by the predicate
    + Click [https://www.ict.griffith.edu.au/aist/Drewer/](https://www.ict.griffith.edu.au/aist/Drewer/) for more
      details

## Results

| Len.  | Dep. |   #R |   #F |   TG |   TD |   MG |   MD |
  | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
|   2   |    1 |   88 |   5M | 37.4 | 15.9 | 4006 |  102 |
|   2   |    5 |  102 |   5M | 37.3 | 15.5 | 4061 |  110 |
|   2   |   10 |  119 |   5M | 41.2 | 18.0 | 3404 |  110 |
|   3   |    1 |   78 |   5M | 39.9 | 28.1 | 2968 |  102 |
|   3   |    5 |  152 |   5M | 39.4 | 15.5 | 3377 |  110 |
|   3   |   10 |   98 |   5M | 38.0 | 16.0 | 3648 |  106 |
|   3   |   10 |   98 |  10M | 80.3 | 28.7 | 2127 |  110 |
|   3   |   10 |   98 |  20M |    - | 52.2 |    - |  110 |
|   3   |   10 |  181 |  10M | 81.1 |    - | 2109 |    - |



## Updated on 9 May, 2022
1. About the rewriting depth

    The argument `rewriting depth` decides the number of iterations of rule learning. Yet the real rewriting depth of the learned rules is unnecessary to be equal to the specified value. On the one hand, the tested systems cannot process recursive rules. So a recursion elimination is needed, which can make the real rewriting depth smaller. On the other hand, a predicate occurs in a rule body can be unexpectedly identical to the predicate of the head atom of another rule, which makes the real rewriting depth larger. In the future, we will manage to control the real rewriting depth of the learned rules.

2. Fixed Benchmarks v.s. Framework of Benchmark Construction

    So far, we have not given any fixed benchmarks but just the framework for benchmark construction. Because the ontologies from rule learning and the datasets to make the answers of tested systems interesting are both dependent on the target queries. In our experiment, we just select 5 CQs from LC-QuAD. Thus, you need to generate your own benchmark based on the queries that you are interested in.

3. If you have any question using the benchmark, feel free to cantact us (bohemianccc@gmail.com). 
    
