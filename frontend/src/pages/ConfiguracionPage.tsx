import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import { Settings, RefreshCw, Calculator, DollarSign, Save } from 'lucide-react'

interface ConfigItem {
  valor: number | string
  tipo: string
  descripcion: string
}

const ConfiguracionPage: React.FC = () => {
  const [config, setConfig] = useState<Record<string, ConfigItem>>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<string | null>(null)

  // Calculadora
  const [calcDistancia, setCalcDistancia] = useState(5.0)
  const [calcVehiculo, setCalcVehiculo] = useState('automovil')
  const [calcCombustible, setCalcCombustible] = useState('gasolina')
  const [calcAsientos, setCalcAsientos] = useState(1)
  const [calcResultado, setCalcResultado] = useState<any>(null)

  const fetchConfig = async () => {
    setLoading(true)
    try {
      const response = await api.get('/api/v1/configuracion/')
      setConfig(response.data)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConfig()
  }, [])

  const handleUpdate = async (clave: string, nuevoValor: string) => {
    setSaving(clave)
    try {
      await api.put(`/api/v1/configuracion/${clave}`, { valor: nuevoValor })
      setConfig((prev) => ({
        ...prev,
        [clave]: {
          ...prev[clave],
          valor:
            prev[clave].tipo === 'float'
              ? parseFloat(nuevoValor)
              : prev[clave].tipo === 'int'
                ? parseInt(nuevoValor)
                : nuevoValor
        }
      }))
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error al actualizar variable')
    } finally {
      setSaving(null)
    }
  }

  const handleReset = async () => {
    if (
      window.confirm(
        '¿Está seguro de restaurar todas las configuraciones a sus valores de fábrica?'
      )
    ) {
      setLoading(true)
      try {
        await api.post('/api/v1/configuracion/reset')
        fetchConfig()
      } catch (error) {
        console.error(error)
        setLoading(false)
      }
    }
  }

  // Lógica local para simular la calculadora basada en las variables del formulario
  const ejecutarCalculadora = () => {
    const vals: Record<string, number> = {}
    Object.keys(config).forEach((k) => {
      vals[k] = parseFloat(config[k].valor as string)
    })

    // Valores por defecto si la configuración aún no está cargada
    const precioGasolina = vals['precio_gasolina_bs_litro'] || 6.5
    const precioDiesel = vals['precio_diesel_bs_litro'] || 3.72
    const precioGas = vals['precio_gas_bs_metro_cubico'] || 2.5

    let consumo = 0.08
    let precio = 6.5

    if (calcCombustible === 'gas') {
      consumo = vals[`consumo_${calcVehiculo}_gas_m3_por_km`] || 0.1
      precio = precioGas
    } else {
      consumo = vals[`consumo_${calcVehiculo}_${calcCombustible}_l_por_km`] || 0.08
      precio = calcCombustible === 'gasolina' ? precioGasolina : precioDiesel
    }

    const costoKm = consumo * precio
    const costoCombustible = calcDistancia * costoKm
    const tarifaBase = vals[`tarifa_base_${calcVehiculo}_bs`] || 3.0
    const subtotal = costoCombustible + tarifaBase

    const asientos = Math.max(calcAsientos, 1)
    const costoPorPasajero = subtotal / asientos

    const comisionPorc = vals['comision_app_porcentaje'] || 15.0
    const comisionApp = costoPorPasajero * (comisionPorc / 100)
    const gananciaConductor = costoPorPasajero - comisionApp

    setCalcResultado({
      costo_combustible: costoCombustible.toFixed(2),
      tarifa_base: tarifaBase.toFixed(2),
      subtotal: subtotal.toFixed(2),
      costo_pasajero: costoPorPasajero.toFixed(2),
      comision_app: comisionApp.toFixed(2),
      ganancia_conductor: gananciaConductor.toFixed(2)
    })
  }

  useEffect(() => {
    if (Object.keys(config).length > 0) {
      ejecutarCalculadora()
    }
  }, [calcDistancia, calcVehiculo, calcCombustible, calcAsientos, config])

  return (
    <div className="flex flex-col gap-8">
      {/* Encabezado */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
            Configuración Global
          </h2>
          <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-1">
            Variables operativas y de precios del sistema de carpooling.
          </p>
        </div>

        <button onClick={handleReset} className="btn btn-secondary shadow-sm">
          <RefreshCw size={18} />
          Valores de Fábrica
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400 font-semibold animate-pulse">
          Cargando configuraciones globales del sistema...
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Formulario de Configuración (2 columnas) */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {/* Combustibles */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-violet-600">
                Precios de Combustibles (Bs/Litro o m³)
              </h3>

              {[
                'precio_gasolina_bs_litro',
                'precio_diesel_bs_litro',
                'precio_gas_bs_metro_cubico'
              ].map((key) => {
                const item = config[key]
                if (!item) return null
                return (
                  <div
                    key={key}
                    className="flex flex-col md:flex-row md:items-center justify-between gap-4 py-2 border-b border-slate-100 dark:border-slate-800 last:border-0"
                  >
                    <div className="flex-1">
                      <span className="text-sm font-bold text-slate-700 dark:text-slate-200 block">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className="text-xs text-slate-400">{item.descripcion}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        defaultValue={item.valor}
                        onBlur={(e) => handleUpdate(key, e.target.value)}
                        disabled={saving === key}
                        step="0.01"
                        className="w-24 text-center py-1.5 px-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 font-bold text-slate-850 dark:text-white"
                      />
                      {saving === key && (
                        <span className="text-xs text-violet-600">Guardando...</span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Consumos de vehículos */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-violet-600">
                Consumos Técnicos (L/km o m³/km)
              </h3>

              {Object.keys(config)
                .filter((k) => k.startsWith('consumo_'))
                .map((key) => {
                  const item = config[key]
                  return (
                    <div
                      key={key}
                      className="flex flex-col md:flex-row md:items-center justify-between gap-4 py-2 border-b border-slate-100 dark:border-slate-800 last:border-0"
                    >
                      <div className="flex-1">
                        <span className="text-sm font-bold text-slate-700 dark:text-slate-200 block">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="text-xs text-slate-400">{item.descripcion}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          defaultValue={item.valor}
                          onBlur={(e) => handleUpdate(key, e.target.value)}
                          disabled={saving === key}
                          step="0.001"
                          className="w-24 text-center py-1.5 px-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 font-bold text-slate-850 dark:text-white"
                        />
                      </div>
                    </div>
                  )
                })}
            </div>

            {/* Tarifas Base y Comisiones */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-violet-600">
                Tarifas y Parámetros del Sistema
              </h3>

              {[
                'tarifa_base_automovil_bs',
                'tarifa_base_moto_bs',
                'comision_app_porcentaje',
                'radio_maximo_caminata_m',
                'penalizacion_cancelacion_porcentaje'
              ].map((key) => {
                const item = config[key]
                if (!item) return null
                return (
                  <div
                    key={key}
                    className="flex flex-col md:flex-row md:items-center justify-between gap-4 py-2 border-b border-slate-100 dark:border-slate-800 last:border-0"
                  >
                    <div className="flex-1">
                      <span className="text-sm font-bold text-slate-700 dark:text-slate-200 block">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className="text-xs text-slate-400">{item.descripcion}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        defaultValue={item.valor}
                        onBlur={(e) => handleUpdate(key, e.target.value)}
                        disabled={saving === key}
                        className="w-24 text-center py-1.5 px-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 font-bold text-slate-850 dark:text-white"
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Calculadora de Preview de Tarifa (1 columna) */}
          <div className="flex flex-col gap-6">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-6 sticky top-24">
              <div className="flex items-center gap-2 text-violet-600 dark:text-violet-400">
                <Calculator size={22} />
                <h3 className="font-extrabold text-slate-800 dark:text-white text-base">
                  Calculadora de Tarifa
                </h3>
              </div>
              <p className="text-xs text-slate-400">
                Simula el desglose de precio de un viaje con las variables vigentes.
              </p>

              <div className="flex flex-col gap-4">
                <div>
                  <label className="label">Distancia (km)</label>
                  <input
                    type="number"
                    value={calcDistancia}
                    onChange={(e) => setCalcDistancia(parseFloat(e.target.value) || 0)}
                    className="input"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="label">Tipo de Vehículo</label>
                  <select
                    value={calcVehiculo}
                    onChange={(e) => setCalcVehiculo(e.target.value)}
                    className="select"
                  >
                    <option value="automovil">🚗 Automóvil</option>
                    <option value="moto">🏍️ Moto</option>
                  </select>
                </div>

                <div>
                  <label className="label">Combustible</label>
                  <select
                    value={calcCombustible}
                    onChange={(e) => setCalcCombustible(e.target.value)}
                    className="select"
                  >
                    <option value="gasolina">Gasolina</option>
                    <option value="diesel">Diésel</option>
                    <option value="gas">G.N.V. (Gas)</option>
                  </select>
                </div>

                <div>
                  <label className="label">Asientos Ocupados</label>
                  <input
                    type="number"
                    value={calcAsientos}
                    onChange={(e) => setCalcAsientos(parseInt(e.target.value) || 1)}
                    className="input"
                    min="1"
                    max="4"
                  />
                </div>
              </div>

              {calcResultado && (
                <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-col gap-3">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Costo Combustible:</span>
                    <span className="font-bold text-slate-700 dark:text-slate-300">
                      {calcResultado.costo_combustible} Bs
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Tarifa Base del Vehículo:</span>
                    <span className="font-bold text-slate-700 dark:text-slate-300">
                      {calcResultado.tarifa_base} Bs
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Subtotal del Viaje:</span>
                    <span className="font-bold text-slate-700 dark:text-slate-300">
                      {calcResultado.subtotal} Bs
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Comisión App:</span>
                    <span className="font-bold text-red-500">{calcResultado.comision_app} Bs</span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Ganancia Conductor (Neto):</span>
                    <span className="font-bold text-emerald-500">
                      {calcResultado.ganancia_conductor} Bs
                    </span>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-dashed border-slate-200 dark:border-slate-700 mt-2">
                    <span className="text-sm font-bold text-slate-850 dark:text-white">
                      Pago del Pasajero:
                    </span>
                    <span className="text-xl font-extrabold text-violet-600 dark:text-violet-400">
                      {calcResultado.costo_pasajero} Bs
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ConfiguracionPage
