# ¿Cómo definir el formato de los nombres de las pruebas?

Todos los tests deben agruparse en clases, cada una relacionada con una clase de tu proyecto. Por ejemplo, si tienes una clase llamada `BankAccount`, la clase de prueba debería llamarse `BankAccountTest`.

Cada prueba debe comenzar con `test_`, para que las herramientas de testing la identifiquen fácilmente.

El siguiente elemento en el nombre debe ser el método que estás probando. Si es un método deposit, el nombre sería `test_deposit_`.

# ¿Cómo estructurar el escenario de la prueba?

Después del método, añade el escenario. Esto se refiere a los valores o parámetros que usas en la prueba. Por ejemplo, en el caso de un valor positivo en un depósito, el escenario sería `positive_amount`.

# ¿Cómo describir el resultado esperado?

Para finalizar el nombre, indica el resultado esperado. Si el depósito incrementa el saldo, añade algo como `increase_balance`. Así, un nombre de prueba completo sería: `test_deposit_positive_amount_increase_balance`.