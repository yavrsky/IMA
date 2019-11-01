# Run tests
SKALE Interchain Message Agent (IMA)


#### Steps to run IMA integration tests


##### Preparations

    - cd proxy    
    - npm install
    
    - cd agent 
    - npm install
    
    - cd npms/skale-ima
    - npm install

add `config.json` to `test` folder (see `config.example.json`) 

!!! both of your accounts (on `mainnet` and `schain`) should have ETH
for contracts deploy on mainnet and schain respectively.

##### run tests

single run test from `test` folder

```
python test.py "tests=<Name of test>"
```
- `<Name of test>` - see inside test file in `test_cases` folder the
  name of test inside `__init__` method
  
example of run `send_erc20_from_schain_to_mainnet.py` test 

```
python test.py "tests=Send ERC20 from schain to mainnet"
```
  

