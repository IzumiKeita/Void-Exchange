# Explicación del Sistema de Tendencias (Flechas y Colores)

Este documento detalla la lógica técnica y funcional detrás de los indicadores de tendencia (flechas rojas y verdes) mostrados en el Dashboard y detalles de ítems.

## 1. Cálculo Matemático (`market_service.py`)

La tendencia se calcula comparando el **precio promedio** del último registro disponible con el registro inmediatamente anterior en el historial de 48 horas.

La fórmula utilizada es:

```python
trend = ((precio_actual - precio_anterior) / precio_anterior) * 100
```

- **precio_actual**: Precio promedio de la última hora registrada.
- **precio_anterior**: Precio promedio de la hora anterior.

El resultado es un **porcentaje** que indica cuánto ha variado el precio.

## 2. Representación Visual (`Dashboard.vue`)

El sistema interpreta este porcentaje para mostrar flechas y colores:

### A. Tendencia Positiva (Flecha Verde ▲)
- **Condición**: El resultado es **mayor o igual a 0** ( `trend >= 0` ).
- **Significado**: El precio del ítem ha **SUBIDO** (o se mantiene igual) respecto a la hora anterior.
- **Interpretación para el Usuario**:
  - **Para Vendedores**: Es un buen momento, el objeto vale más.
  - **Para Compradores**: El objeto está encareciéndose.

### B. Tendencia Negativa (Flecha Roja ▼)
- **Condición**: El resultado es **negativo** ( `trend < 0` ).
- **Significado**: El precio del ítem ha **BAJADO** respecto a la hora anterior.
- **Interpretación para el Usuario**:
  - **Para Vendedores**: El objeto está perdiendo valor.
  - **Para Compradores**: Es una oportunidad de oferta, está más barato.

## 3. Ejemplo Práctico

Si un Warframe "Rhino Prime Set":
- Hora anterior valía: **100 pl**
- Hora actual vale: **90 pl**

Cálculo: `(90 - 100) / 100 * 100 = -10%`

**Resultado en pantalla**:
- **Flecha**: ▼ (Abajo)
- **Color**: Rojo
- **Valor**: -10%
- **Lectura**: El precio ha caído un 10%.

## 4. Notas Técnicas
- Si no hay datos previos (es el primer registro), la tendencia es 0%.
- El sistema redondea el porcentaje a 2 decimales.
- Esta lógica se aplica consistentemente tanto en el Dashboard como en el Chat de IA para las recomendaciones.
