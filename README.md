![logo](https://github.com/sajji18/TinkerQuest-24/blob/main/media/logo.jpeg)

#

<div align="center">

</div>

# DocAI



<br>

## 💻 Using DocAI


```python3
import pybamm

model = pybamm.lithium_ion.DFN()  # Doyle-Fuller-Newman model
sim = pybamm.Simulation(model)
sim.solve([0, 3600])  # solve for 1 hour
sim.plot()
```

```python3
import pybamm

experiment = pybamm.Experiment(
    [
        (
            "Discharge at C/10 for 10 hours or until 3.3 V",
            "Rest for 1 hour",
            "Charge at 1 A until 4.1 V",
            "Hold at 4.1 V until 50 mA",
            "Rest for 1 hour",
        )
    ]
    * 3,
)
model = pybamm.lithium_ion.DFN()
sim = pybamm.Simulation(model, experiment=experiment, solver=pybamm.CasadiSolver())
sim.solve()
sim.plot()
```

## 🚀 Installing 

Install

```bash
  npm install my-project
  cd my-project
```
    

### Using pip


## 📖 



## 🛠️
## 📫 

## 📃 

## ✨ 
