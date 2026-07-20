# Fórmulas Matemáticas del Sistema Apuradito

## 1. Fórmula de Costo de Combustible por km

```
costo_combustible_km = consumo_vehiculo_L_por_km × precio_combustible_Bs_litro
```

### Valores por defecto (editables desde admin):
| Vehículo | Combustible | Consumo (L/km) | Precio Bs/L | Costo Bs/km |
|----------|-------------|----------------|-------------|-------------|
| Automóvil | Gasolina | 0.08 | 6.50 | 0.52 |
| Automóvil | Diésel | 0.065 | 3.72 | 0.24 |
| Automóvil | Gas | 0.10 (m³) | 2.50 | 0.25 |
| Moto | Gasolina | 0.03 | 6.50 | 0.195 |

## 2. Fórmula Maestra de Costo de Viaje

```
costo_combustible_tramo = distancia_km × costo_combustible_km
tarifa_base = tarifa_base_{tipo_vehiculo}_bs  (configurable desde admin)
subtotal_ruta = costo_combustible_tramo + tarifa_base

costo_por_pasajero = subtotal_ruta / max(asientos_ocupados_en_tramo, 1)
comision_app_Bs = costo_por_pasajero × (comision_app_% / 100)
ganancia_conductor_Bs = costo_por_pasajero - comision_app_Bs
```

**Nota:** El pasajero paga `costo_por_pasajero`. El conductor recibe `ganancia_conductor_Bs`. La app retiene `comision_app_Bs`.

## 3. Score de Optimalidad de Ruta

```
score = (1000 / (dist_caminata_abordaje_m + 1)) × 0.4
      + (1000 / (dist_caminata_desabordaje_m + 1)) × 0.4
      + (100 / (costo_Bs + 1)) × 0.2
```

- **Mayor score = más óptima la ruta**
- Desempate: se muestra primero la ruta con menor precio

## 4. Penalización por Cancelación

```
penalizacion_Bs = costo_viaje_Bs × (penalizacion_cancelacion_% / 100)
```

- Default: 10% del costo del viaje
- Aplica al que cancela (conductor o pasajero)
- Se debita de saldo coins; si no tiene, queda como deuda

## 5. Variables Configurables desde Admin

| Clave | Valor Default | Descripción |
|-------|--------------|-------------|
| precio_gasolina_bs_litro | 6.50 | Precio Bs por litro de gasolina |
| precio_diesel_bs_litro | 3.72 | Precio Bs por litro de diésel |
| precio_gas_bs_metro_cubico | 2.50 | Precio Bs por m³ de gas |
| consumo_automovil_gasolina_l_por_km | 0.08 | L/km automóvil gasolina |
| consumo_automovil_diesel_l_por_km | 0.065 | L/km automóvil diésel |
| consumo_automovil_gas_m3_por_km | 0.10 | m³/km automóvil gas |
| consumo_moto_gasolina_l_por_km | 0.03 | L/km moto gasolina |
| tarifa_base_automovil_bs | 3.00 | Tarifa mínima automóvil (Bs) |
| tarifa_base_moto_bs | 2.00 | Tarifa mínima moto (Bs) |
| comision_app_porcentaje | 15.0 | % comisión de la app |
| tipo_cambio_bs_usd | 6.86 | Tipo de cambio Bs/USD |
| radio_maximo_caminata_m | 800 | Radio búsqueda rutas (metros) |
| limite_rutas_pasajero | 10 | Máx rutas mostradas al pasajero |
| meses_morosidad_congelamiento | 2 | Meses deuda para congelar cuenta |
| penalizacion_cancelacion_porcentaje | 10.0 | % penalización por cancelar |
