import pytest

# Test SensorData class:
'''
# Rules:
1. `factor` and `offset` can be edited and read directly, as they only affect the result of `get_value()`;
2. `raw_value` can also be edited and read directly, as it is the basis for calculating the calibrated value;
3. `factor` must be always applyed first, then `offset` to the raw value to get the calibrated value in `get_value()`;
4. `get_value()` returns the calibrated value, calculated as `raw_value * factor + offset`;
5. `_isolated` and `_agree_count` can be read directly, but should not be edited directly;
6. The raw and calibrated values must always be int;
7. `_agree_count` stores the number of consecutive agreements (positive) or disagreements (negative) with the majority (ruled by the NMR). It must reset to 0 when the agreement status alters (from agreement to disagreement or vice versa);
'''


# Test NMR class:
'''
# Rules:

from portuguese:
```
O sistema votador deve receber as informações dos sensores via rede, decidir e mostrar a
temperatura do TEMPTF. Caso o valor de um dos sensores seja divergente em pelo menos
10% em relação a média aritmética (x) dos valores recebidos, indicar que houve
mascaramento de falhas. Caso contrário, mostre a menor temperatura recebida, indicando
consenso;
• Caso o mesmo sensor tenha medições divergentes por três (3) ciclos consecutivos de
medição em relação a x, indicar em tela que o sensor pode estar comprometido e, portanto,
foi isolado. Neste ponto em diante, considerar para a resposta final do TEMPTF apenas os
resultados de dois (2) sensores indicando que o sistema encontra-se degradado. Caso os
valores sejam diferentes em pelo menos 10 %, indicar que o sistema se tornou instável e
apresentar a última medição segura recebida.
• Continuar a monitorar os dados dos sensores, mesmo dos comprometidos. Voltar a mostrar
um valor recebido via rede quando dois sensores não comprometidos concordarem (valores
divergentes em menos de 10 %) em pelo menos três (3) medições consecutivas.
• O TEMPTF pode voltar a mostrar os dados em consenso (considerando todos os sensores),
caso as três leituras não sejam divergentes em pelos menos 10% em relação a x por três (3)
ciclos consecutivos.
```

To English (NMR focused):
> (note we are developing a NMR system instead of a TMR, and the parameters are configurable)
1. `tolerance` is a percentage value that defines how close the sensor readings must be to the mean of active sensors to be considered in agreement;
2. `isolation_steps` is the number of consecutive disagreements required before a sensor is isolated;
3. `recovery_steps` is the number of consecutive agreements required before an isolated sensor is recovered;
4. When the NMR cannot determine a valid reading it must return the `failsafe` value and log the instability even if it is not in verbose mode;
5. The NMR must continuously monitor all sensors, including isolated ones, and update their agreement status based on the defined rules;
6. The NMR must return the minimum value of active sensors in consensus.
7. It must log the state changes of all sensors (agreement, disagreement, isolation, recovery) when in verbose mode.
8. The NMR should be able to handle any number of sensors;
9. When in degraded mode it should return the last safe value until it can return to normal operation or all sensors are isolated;
10. Masked failures should be logged only 
'''