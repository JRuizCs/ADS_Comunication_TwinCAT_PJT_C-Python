using System;
using TwinCAT.Ads;

namespace AdsApp
{
    internal class Program
    {
        private static void Main(string[] args)
        {
            // Instancia el cliente para gestionar la comunicacion mediante el protocolo ADS.
            using (AdsClient client = new AdsClient())
            {
                // Establece la conexion de red hacia el servidor ADS utilizando el AMS Net ID especifico y el puerto del Runtime 1.
                client.Connect("10.55.128.28.1.1", 851);

                // Valida el estado de la conexion TCP/IP antes de iniciar el ciclo principal de la aplicacion.
                if (!client.IsConnected)
                {
                    Console.WriteLine("Error: No se pudo establecer la conexion ADS con el PLC.");
                    return;
                }

                bool ejecutando = true;

                while (ejecutando)
                {   Console.WriteLine("\n==================================================");
                    Console.WriteLine("\n==================================================");
                    Console.WriteLine("\n==================================================");
                    Console.WriteLine("        EJEMPLO TWINCAT ADS .NET           ");
                    Console.WriteLine("==================================================");
                    Console.WriteLine("--- GESTION DE ARRAY (MAIN.aBuffer) ---");
                    Console.WriteLine(" 1. Leer todo el array");
                    Console.WriteLine(" 2. Escribir valor en un indice especifico (0-9)");
                    Console.WriteLine(" 3. Rellenar todo el array con un mismo valor");
                    Console.WriteLine("\n--- GESTION DE ESTRUCTURA (MAIN.stSensor) ---");
                    Console.WriteLine(" 4. Leer estructura completa");
                    Console.WriteLine(" 5. Modificar estado (bActive) [BOOL]");
                    Console.WriteLine(" 6. Modificar identificador (nId) [INT]");
                    Console.WriteLine(" 7. Modificar valor de lectura (fValue) [REAL]");
                    Console.WriteLine(" 8. Modificar nombre del sensor (sName) [STRING]");
                    Console.WriteLine(" 9. Escribir valor en array (aValues) [0-4]");
                    Console.WriteLine("\n 0. Desconectar y Salir");
                    Console.WriteLine("==================================================");
                    Console.Write("Seleccione una accion: ");
                    


                    string opcion = Console.ReadLine();

                    try
                    {
                        switch (opcion)
                        {
                            case "1":
                                uint handleBufferRead = client.CreateVariableHandle("MAIN.aBuffer");

                                int[] bufferLeido = (int[])client.ReadAny(handleBufferRead, typeof(int[]), new int[] { 10 });

                                Console.WriteLine($"\n[Lectura] MAIN.aBuffer: [{string.Join(", ", bufferLeido)}]");

                                client.DeleteVariableHandle(handleBufferRead);
                                break;

                            case "2":
                                Console.Write("\nIntroduzca el indice del array a modificar (0-9): ");
                                
                                if (int.TryParse(Console.ReadLine(), out int indiceA) && indiceA >= 0 && indiceA <= 9)
                                {
                                    Console.Write($"Introduzca el nuevo valor entero para aBuffer[{indiceA}]: ");
                                    if (int.TryParse(Console.ReadLine(), out int nuevoValorA))
                                    {
                                        uint handleBufferWrite = client.CreateVariableHandle("MAIN.aBuffer");
                                        int[] bufferAEditar = (int[])client.ReadAny(handleBufferWrite, typeof(int[]), new int[] { 10 });

                                        bufferAEditar[indiceA] = nuevoValorA;

                                        client.WriteAny(handleBufferWrite, bufferAEditar);
                                        Console.WriteLine($"\n[Escritura] MAIN.aBuffer[{indiceA}] actualizado a {nuevoValorA}.");

                                        client.DeleteVariableHandle(handleBufferWrite);
                                    }
                                    else
                                    {
                                        Console.WriteLine("\n[Error] El valor introducido no es un numero entero valido.");
                                    }
                                }
                                else
                                {
                                    Console.WriteLine("\n[Error] Indice fuera de rango o formato incorrecto.");
                                }
                                break;

                            case "3":
                                Console.Write("\nIntroduzca el valor para rellenar todo el array aBuffer: ");
                                if (int.TryParse(Console.ReadLine(), out int valorRelleno))
                                {
                                    uint handleBufferFill = client.CreateVariableHandle("MAIN.aBuffer");
                                    
                                    int[] bufferLleno = new int[10];
                                    for (int i = 0; i < bufferLleno.Length; i++)
                                    {
                                        bufferLleno[i] = valorRelleno;
                                    }

                                    client.WriteAny(handleBufferFill, bufferLleno);
                                    Console.WriteLine($"\n[Escritura] Todo el array MAIN.aBuffer ha sido sobreescrito con el valor {valorRelleno}.");

                                    client.DeleteVariableHandle(handleBufferFill);
                                }
                                else
                                {
                                    Console.WriteLine("\n[Error] Formato numerico invalido.");
                                }
                                break;

                            case "4":
                                uint handleStructRead = client.CreateVariableHandle("MAIN.stSensor");

                                ST_SensorData sensorLeido = (ST_SensorData)client.ReadAny(handleStructRead, typeof(ST_SensorData));

                                Console.WriteLine("\n[Lectura] Datos actuales de MAIN.stSensor:");
                                Console.WriteLine($"  - bActive : {sensorLeido.bActive}");
                                Console.WriteLine($"  - nId     : {sensorLeido.nId}");
                                Console.WriteLine($"  - fValue  : {sensorLeido.fValue}");
                                Console.WriteLine($"  - sName   : {sensorLeido.sName}");
                                Console.WriteLine($"  - aValues : [{string.Join(", ", sensorLeido.aValues)}]");

                                client.DeleteVariableHandle(handleStructRead);
                                break;

                            case "5":
                                uint handleStructBool = client.CreateVariableHandle("MAIN.stSensor");
                                ST_SensorData sensorABool = (ST_SensorData)client.ReadAny(handleStructBool, typeof(ST_SensorData));

                                sensorABool.bActive = !sensorABool.bActive;

                                client.WriteAny(handleStructBool, sensorABool);
                                Console.WriteLine($"\n[Escritura] MAIN.stSensor.bActive ha conmutado a: {sensorABool.bActive}");

                                client.DeleteVariableHandle(handleStructBool);
                                break;

                            case "6":
                                Console.Write("\nIntroduzca un nuevo valor INT para stSensor.nId: ");
                                if (short.TryParse(Console.ReadLine(), out short nuevoId))
                                {
                                    uint handleStructId = client.CreateVariableHandle("MAIN.stSensor");
                                    ST_SensorData sensorAId = (ST_SensorData)client.ReadAny(handleStructId, typeof(ST_SensorData));

                                    sensorAId.nId = nuevoId;

                                    client.WriteAny(handleStructId, sensorAId);
                                    Console.WriteLine($"\n[Escritura] MAIN.stSensor.nId actualizado a: {sensorAId.nId}");

                                    client.DeleteVariableHandle(handleStructId);
                                }
                                else
                                {
                                    Console.WriteLine("\n[Error] Valor no valido para tipo INT (short de 16 bits).");
                                }
                                break;

                            case "7":
                                Console.Write("\nIntroduzca un nuevo valor REAL para stSensor.fValue (use coma o punto segun su SO): ");
                                if (float.TryParse(Console.ReadLine(), out float nuevoFloat))
                                {
                                    uint handleStructFloat = client.CreateVariableHandle("MAIN.stSensor");
                                    ST_SensorData sensorAFloat = (ST_SensorData)client.ReadAny(handleStructFloat, typeof(ST_SensorData));

                                    sensorAFloat.fValue = nuevoFloat;

                                    client.WriteAny(handleStructFloat, sensorAFloat);
                                    Console.WriteLine($"\n[Escritura] MAIN.stSensor.fValue actualizado a: {sensorAFloat.fValue}");

                                    client.DeleteVariableHandle(handleStructFloat);
                                }
                                else
                                {
                                    Console.WriteLine("\n[Error] Valor no valido para tipo REAL (float de 32 bits).");
                                }
                                break;

                            case "8":
                                Console.Write("\nIntroduzca el nuevo texto para stSensor.sName (Max 80 caracteres): ");
                                string nuevoNombre = Console.ReadLine();
                                
                                uint handleStructStr = client.CreateVariableHandle("MAIN.stSensor");
                                ST_SensorData sensorAStr = (ST_SensorData)client.ReadAny(handleStructStr, typeof(ST_SensorData));

                                if (nuevoNombre.Length > 80) nuevoNombre = nuevoNombre.Substring(0, 80);
                                sensorAStr.sName = nuevoNombre;

                                client.WriteAny(handleStructStr, sensorAStr);
                                Console.WriteLine($"\n[Escritura] MAIN.stSensor.sName actualizado a: {sensorAStr.sName}");

                                client.DeleteVariableHandle(handleStructStr);
                                break;

                            case "9":
                                Console.Write("\nIntroduzca el indice del array interno aValues a modificar (0-4): ");
                                if (int.TryParse(Console.ReadLine(), out int indiceIn) && indiceIn >= 0 && indiceIn <= 4)
                                {
                                    Console.Write($"Introduzca el nuevo valor entero para aValues[{indiceIn}]: ");
                                    if (short.TryParse(Console.ReadLine(), out short nuevoValorIn))
                                    {
                                        uint handleStructArr = client.CreateVariableHandle("MAIN.stSensor");
                                        ST_SensorData sensorAArr = (ST_SensorData)client.ReadAny(handleStructArr, typeof(ST_SensorData));

                                        sensorAArr.aValues[indiceIn] = nuevoValorIn;

                                        client.WriteAny(handleStructArr, sensorAArr);
                                        Console.WriteLine($"\n[Escritura] MAIN.stSensor.aValues[{indiceIn}] actualizado a {nuevoValorIn}.");

                                        client.DeleteVariableHandle(handleStructArr);
                                    }
                                    else
                                    {
                                        Console.WriteLine("\n[Error] Valor no valido para el tipo INT (short).");
                                    }
                                }
                                else
                                {
                                    Console.WriteLine("\n[Error] Indice fuera de rango o formato incorrecto.");
                                }
                                break;

                            case "0":
                                ejecutando = false;
                                Console.WriteLine("\nFinalizando ejecucion y cerrando canal ADS...");
                                break;

                            default:
                                Console.WriteLine("\n[Error] Opcion no reconocida. Seleccione un numero del menu.");
                                break;
                        }
                    }
                    catch (AdsErrorException adsEx)
                    {
                        Console.WriteLine($"\n[Excepcion ADS] Codigo de error: {adsEx.ErrorCode} - Mensaje: {adsEx.Message}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"\n[Excepcion General] {ex.Message}");
                    }
                }

                // Fuerza la desconexion del socket TCP asociado al cliente liberando el puerto del sistema operativo.
                client.Disconnect();
            }
        }
    }
}