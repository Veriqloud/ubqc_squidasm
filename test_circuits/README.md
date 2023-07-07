## 1. Drawings of test circuits

![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_1.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_2.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_3.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_4.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_5.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_6.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_7.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_8.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_9.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_10.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_11.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_12.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_13.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_14.png?raw=true)
![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/test_circuits/circuit_15.png?raw=true)

## 2. Classification of circuits

|Circuit| Expected Outcome|#Qubits|#Computational qubits|#Measurements|#Entanglements|
| ----- |-------|------|------|------|------|
|1      | **[0]**   | 1    | 2    | 1    |  1   |
|2      | **[0]**   | 1    | 2    | 1    |  1   |
|3      | **[0]**   | 1    | 4    | 3    |  3   |
|4      | **[0,1]**   | 2    | 4    | 2    |  2   |
|5      | **[1,1]**   | 2    | 6    | 4    |  5   |
|6      | **[1,0]**   | 2    | 10    | 8    |  11   |
|7      | **[1,1,0]**   | 3    | 6    | 3    |  3   |
|8      | **[1,1,1]**   | 3    | 6    | 5    |  6   |
|9      | **[0,1,1]**   | 3    | 10    | 7    |  9  |
|10      | **[1,1,0,0]**   | 4    | 8    | 4    |  4   |
|11      | **[1,1,1,1]**   | 4    | 10    | 6    |  7   |
|12      | **[1,1,1,1]**   | 4    | 12    | 8    |  9   |
|13      | **[1,1,0,0,0]**   | 5    | 10    | 5    |  8   |
|14      | **[1,1,1,1,0]**   | 5    | 14    | 9    |  10   |
|15      | **[0,1,1,1,1]**   | 5    | 18    | 13    |  15   |

## 3. Performance

|Circuit/Iteration|Mean (default noise)|STD (default noise)|Mean (customized noise) | STD (customized noise) |
|----|----|----|----|----|
1|**98.6**| 1.0 | **70.6** | 4.2
2       |**98.0** | 1.3 | **59.8** | 6.3
3       |**94.8** | 1.9 | **68.5** | 5.9
4       |**94.8** | 2.1 | **46.6** | 6.5
5         |**91.7** | 2.1 | **38.4** | 3.8
6        |**82.3**|  3.1 | **25.6** | 2.2
7      |**92.8** | 3.1 | **37.4** | 4.6
8          |**91.8**| 2.4 | **26.9** | 3.2
9         |**86.1** | 3.9 | **23.0** | 3.5
10         |**89.1** | 2.8 | **25.1** | 3.8
11         |**87.8** | 3.2 | **18.9** | 2.8
12       |**85.6** | 3.0 | **14.0** | 3.2
13        |**89.7** | 3.3 | **17.2** | 5.2
14        |**82.8** | 3.8 | **12.0** | 3.0
15         |**78.9** | 5.1| **8.4** | 3.2

All results here refer to the success rate out of 100 iterations for a given circuit.



