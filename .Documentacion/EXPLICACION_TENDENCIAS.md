# Explicación de Indicadores de Tendencia

Este documento detalla el significado de las flechas y porcentajes que aparecen en las tarjetas de items en el Dashboard.

## ¿Qué representan?

Los indicadores de tendencia muestran la **variación del precio promedio** del ítem en el corto plazo (basado en el historial de las últimas 48 horas).

### 🟢 Flecha Verde con Valor Positivo (ej. ▲ 4.12%)
*   **Significado:** El precio promedio del ítem ha **SUBIDO** recientemente.
*   **Cálculo:** Se compara el precio promedio del último registro disponible con el precio promedio del registro inmediatamente anterior.
*   **Interpretación:** La demanda podría estar aumentando o la oferta disminuyendo, empujando el precio hacia arriba.

### 🔴 Flecha Roja con Valor Negativo (ej. ▼ -9.09%)
*   **Significado:** El precio promedio del ítem ha **BAJADO** recientemente.
*   **Cálculo:** Al igual que el positivo, compara el último precio promedio con el anterior, pero el resultado indica una caída.
*   **Interpretación:** Puede haber un exceso de oferta (muchos vendedores) o menor interés, lo que hace que el precio caiga.

## Fórmula Técnica

El sistema utiliza los datos de estadísticas de 48 horas (`48hours`) de Warframe Market.

```python
Tendencia = ((Precio_Actual - Precio_Anterior) / Precio_Anterior) * 100
```

*   **Precio_Actual**: El `avg_price` (precio promedio) del último punto de datos disponible.
*   **Precio_Anterior**: El `avg_price` del penúltimo punto de datos.

> **Nota:** Este indicador es muy sensible a cambios recientes y sirve para detectar movimientos inmediatos en el mercado.
