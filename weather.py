# Full MicroPython Weather Server Code with Manual Capitalization, Timing, and Chunked Sending

import network
import time
import urequests
import socket
import utime
import gc # Garbage collector, useful on constrained devices
import sys # For more detailed error printing

# --- Configuration ---
WIFI_SSID = "WIFI NAME" # <<< Replace with your Network Name
WIFI_PASSWORD = "PASSWORD" # <<< # <<< Replace with your Passkey
OPENWEATHERMAP_API_KEY = "API_KEY"  # <<< Replace with your OpenWeatherMap API key
CITY = "Halifax,gb"  # <<< Replace with your desired city and country code (e.g., "London,uk", "New York,us")
# --- End Configuration ---

# Connect to Wi-Fi
def connect_wifi(ssid, password):
    """Connects to the Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to network '{ssid}'...")
        wlan.connect(ssid, password)

        max_wait = 15 # Increased wait time slightly
        while not wlan.isconnected() and max_wait > 0:
            print(".", end="")
            time.sleep(1)
            max_wait -= 1

        if wlan.isconnected():
            print("\nConnected! Network config:", wlan.ifconfig())
            return wlan
        else:
            print("\nConnection failed.")
            return None
    else:
        print("Already connected. Network config:", wlan.ifconfig())
        return wlan

# Fetch Weather Data
def get_weather(city, api_key):
    """Fetches weather data from OpenWeatherMap API using manual capitalization."""
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    print(f"Requesting weather URL: {url}")
    response = None  # Initialize response to None
    try:
        response = urequests.get(url, timeout=10) # Add timeout
        status_code = response.status_code
        data = response.json() # Parse JSON immediately
        response.close() # Close response ASAP to free memory

        print(f"Raw data for {city}: {data}")  # Debugging

        if status_code == 200:
            # Extract data safely using .get() to avoid KeyErrors
            weather_data = data.get('weather', [{}])[0] # Get first weather item safely
            main_data = data.get('main', {})
            wind_data = data.get('wind', {})
            sys_data = data.get('sys', {})

            weather_desc = weather_data.get('description', 'N/A') # Default if missing
            temperature = main_data.get('temp')
            feels_like = main_data.get('feels_like')
            humidity = main_data.get('humidity')
            pressure = main_data.get('pressure')
            wind_speed = wind_data.get('speed')
            wind_direction = wind_data.get('deg')
            visibility = data.get('visibility') # Visibility is top-level
            sunrise = sys_data.get('sunrise')
            sunset = sys_data.get('sunset')
            country = sys_data.get('country')
            city_name = data.get('name')

            # Check if essential data was retrieved
            if temperature is None or sunrise is None or sunset is None or not city_name:
                 print("Essential weather data missing from API response.")
                 return (None,) * 12 # Return tuple of Nones matching expected output

            # Convert Unix timestamps to time (use utime.gmtime for UTC)
            try:
                sunrise_time = utime.gmtime(sunrise)
                sunset_time = utime.gmtime(sunset)
                # Format time (HH:MM:SS) - Indices: 3=hour, 4=minute, 5=second
                sunrise_str = f"{sunrise_time[3]:02}:{sunrise_time[4]:02}:{sunrise_time[5]:02}"
                sunset_str = f"{sunset_time[3]:02}:{sunset_time[4]:02}:{sunset_time[5]:02}"
            except Exception as e:
                print(f"Error formatting time: {e}")
                sunrise_str = "N/A"
                sunset_str = "N/A"

            # --- MANUAL CAPITALIZATION WORKAROUND ---
            temp_desc = str(weather_desc) # Ensure it's treated as a string sequence
            weather_capitalized = "" # Initialize
            if temp_desc: # Check if the string is not empty
                try:
                    # Manually capitalize: first char uppercase, rest lowercase
                    first_char = temp_desc[0]
                    rest_of_string = temp_desc[1:]
                    # Ensure upper() and lower() exist and work as expected
                    if hasattr(first_char, 'upper') and hasattr(rest_of_string, 'lower'):
                         weather_capitalized = first_char.upper() + rest_of_string.lower()
                    else:
                         print("Warning: '.upper()' or '.lower()' missing from string type!")
                         weather_capitalized = temp_desc # Fallback if methods missing
                except IndexError: # Handle potential empty string issue if check failed
                    weather_capitalized = temp_desc
                except Exception as cap_err:
                    print(f"Error during manual capitalization: {cap_err}")
                    weather_capitalized = temp_desc # Fallback to original if manual fails
            else:
                 weather_capitalized = temp_desc # Keep it empty if it was empty
            # --- END WORKAROUND ---

            # Convert visibility from meters to km, handle if None or non-numeric
            try:
                visibility_km = f"{visibility / 1000:.1f}" if visibility is not None else 'N/A'
            except TypeError:
                visibility_km = 'N/A'
            except Exception as vis_err:
                print(f"Error processing visibility: {vis_err}")
                visibility_km = 'N/A'

            # Provide defaults for potentially missing numeric/string values for display
            feels_like = feels_like if feels_like is not None else 'N/A'
            humidity = humidity if humidity is not None else 'N/A'
            pressure = pressure if pressure is not None else 'N/A'
            wind_speed = wind_speed if wind_speed is not None else 'N/A'
            wind_direction = wind_direction if wind_direction is not None else 'N/A'
            country = country if country else 'N/A'

            return (weather_capitalized, temperature, feels_like, humidity, pressure,
                    wind_speed, wind_direction, visibility_km, sunrise_str, sunset_str,
                    country, city_name)
        else:
            print(f"Error fetching weather: Status code {status_code}")
            # Try to get text content for error diagnosis
            error_text = ""
            try:
                error_text = response.text
            except Exception as text_err:
                print(f"Could not read response text: {text_err}")
            print(f"Response content: {error_text if error_text else '(Could not get text)'}")
            return (None,) * 12 # Return tuple of Nones

    except Exception as e:
        # Print the specific error triggering this block
        print(f"An error occurred in get_weather function: {e}")
        # Print traceback for more detailed error location (if sys module has print_exception)
        try:
             sys.print_exception(e)
        except AttributeError:
             print("(Traceback printing not available in this MicroPython build)")
        except Exception as tb_err:
             print(f"(Error trying to print traceback: {tb_err})")

        # Ensure response is closed if an error happened after it was opened
        if response:
            try:
                response.close()
            except Exception as close_e:
                print(f"Error closing response: {close_e}")
        return (None,) * 12 # Return tuple of Nones
    finally:
        # Explicitly run garbage collection after network requests
        gc.collect()


# Set up the web server
def start_server():
    """Starts the web server on port 80."""
    try:
        # Force garbage collection before attempting to bind socket
        gc.collect()
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]  # Bind to port 80
        s = socket.socket()
        # Allow reusing address quickly after script restart
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(1) # Listen for only 1 connection at a time
        print('Web server listening on', addr)
        return s
    except OSError as e:
        print(f"Error starting server (OSError): {e}")
        print("Port 80 might be in use or unavailable. Check network state.")
        return None
    except Exception as e:
        print(f"Unexpected error starting server: {e}")
        try:
             sys.print_exception(e)
        except Exception:
            pass # Ignore if traceback printing fails
        return None


# Main Application
def run_app():
    """Main application function with timing and chunked sending."""
    wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)

    if not wlan or not wlan.isconnected():
        print("Could not connect to Wi-Fi. Halting.")
        return # Stop execution if no Wi-Fi

    server = start_server()
    if not server:
        print("Could not start web server. Halting.")
        return # Stop execution if server fails

    while True:
        cl = None # Initialize client socket variable
        client_addr = None
        try:
            print(f"\nWaiting for client connection... (Free memory: {gc.mem_free()})")
            cl, client_addr = server.accept()
            cl.settimeout(10.0) # Timeout for client operations (recv/send)
            print(f'Client connected from {client_addr}')

            # --- Receive Request (Basic handling) ---
            request = None
            try:
                # Read the first line which is usually enough for GET
                request_line_bytes = cl.readline()
                if not request_line_bytes:
                    print("Client disconnected before sending request.")
                    cl.close()
                    continue

                request_line = request_line_bytes.decode('utf-8').strip()
                print(f"--- Request Line --- \n{request_line}\n--------------------")

                # Clear any remaining headers from the buffer (optional but good practice)
                # while True:
                #    header = cl.readline()
                #    if not header or header == b'\r\n':
                #        break

            except OSError as e:
                print(f"Timeout or error receiving request: {e.args[0]}") # Print errno
                if cl: cl.close() # Ensure socket is closed
                continue # Wait for next connection
            except Exception as e:
                 print(f"Error receiving/decoding request: {e}")
                 if cl: cl.close()
                 continue

            # --- Get Weather Data ---
            print("Fetching weather data...")
            gc.collect() # Collect garbage before potentially long operation
            start_time = time.ticks_ms() # <<< START TIMER
            weather_results = get_weather(CITY, OPENWEATHERMAP_API_KEY)
            end_time = time.ticks_ms() # <<< END TIMER
            duration = time.ticks_diff(end_time, start_time) # <<< CALCULATE DURATION
            print(f"Weather data fetched in {duration} ms.") # <<< PRINT DURATION
            gc.collect() # Collect again after get_weather's internal collection

            # Unpack the tuple (or Nones if failed)
            (weather, temperature, feels_like, humidity, pressure, wind_speed,
             wind_direction, visibility_km, sunrise_str, sunset_str, country, city_name) = weather_results

            # --- Prepare and Send HTTP Response ---
            try:
                # Send Headers
                print("Sending HTTP headers...")
                cl.send(b'HTTP/1.1 200 OK\r\n') # Use bytes directly
                cl.send(b'Content-Type: text/html; charset=UTF-8\r\n')
                cl.send(b'Connection: close\r\n') # Tell client we will close connection
                cl.send(b'\r\n') # End of headers
                print("Headers sent.")
                gc.collect() # GC before building large string

                # --- Generate HTML Body ---
                print("Generating HTML body...")
                if city_name and temperature is not None: # Check if essential data is present
                    # Ensure all parts are strings before formatting
                    temperature_str = str(temperature)
                    feels_like_str = str(feels_like)
                    humidity_str = str(humidity)
                    pressure_str = str(pressure)
                    wind_speed_str = str(wind_speed)
                    wind_direction_str = str(wind_direction)
                    visibility_km_str = str(visibility_km)
                    weather_str = str(weather)
                    sunrise_str_disp = str(sunrise_str)
                    sunset_str_disp = str(sunset_str)
                    country_str = str(country)
                    city_name_str = str(city_name)


                    # Define parts of the HTML to send in chunks
                    # Chunk 1: Head and start of body/container
                    html_head = f"""<!DOCTYPE html>
                    <html><head><title>Weather in {city_name_str}</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
                    body {{ font-family: Arial, sans-serif; background-color: #f0f0f0; color: #333; margin: 0; padding: 15px; }}
                    .container {{ max-width: 600px; margin: 20px auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    h1 {{ color: #2a9d8f; text-align: center; font-size: 1.5em; }} p {{ margin: 8px 0; line-height: 1.4; font-size: 0.95em; }}
                    .weather {{ font-size: 1.1em; font-weight: bold; color: #e76f51; }} .temp {{ font-size: 2em; font-weight: bold; text-align: center; color: #f77f00; margin-bottom: 15px; }}
                    .label {{ font-weight: bold; color: #555; min-width: 90px; display: inline-block; }}
                    </style></head><body><div class="container">
                    <h1>Weather in {city_name_str}, {country_str}</h1>
                    <p class="temp">{temperature_str}°C</p>"""

                    # Chunk 2: Main weather details
                    html_details = f"""<p><span class="label">Condition:</span> <span class="weather">{weather_str}</span></p>
                    <p><span class="label">Feels Like:</span> {feels_like_str}°C</p>
                    <p><span class="label">Humidity:</span> {humidity_str}%</p>
                    <p><span class="label">Pressure:</span> {pressure_str} hPa</p>
                    <p><span class="label">Wind:</span> {wind_speed_str} m/s at {wind_direction_str}°</p>
                    <p><span class="label">Visibility:</span> {visibility_km_str} km</p>
                    <p><span class="label">Sunrise:</span> {sunrise_str_disp} UTC</p>
                    <p><span class="label">Sunset:</span> {sunset_str_disp} UTC</p>"""

                    # Chunk 3: Closing tags
                    html_foot = "</div></body></html>"

                    # --- Send HTML Body in Chunks ---
                    print("Sending HTML body chunks...")
                    chunk1 = html_head.encode('utf-8')
                    cl.send(chunk1)
                    print(f"Sent chunk 1 ({len(chunk1)} bytes)")
                    time.sleep(0.01) # Small delay might help some network stacks
                    gc.collect() # GC between chunks

                    chunk2 = html_details.encode('utf-8')
                    cl.send(chunk2)
                    print(f"Sent chunk 2 ({len(chunk2)} bytes)")
                    time.sleep(0.01)
                    gc.collect()

                    chunk3 = html_foot.encode('utf-8')
                    cl.send(chunk3)
                    print(f"Sent chunk 3 ({len(chunk3)} bytes)")

                    print("Full response body sent.")

                else:
                     # Send error page (can also be chunked if large, but usually isn't)
                     print("Generating/Sending error HTML...")
                     html_body = """<!DOCTYPE html><html><head><title>Weather Error</title><meta charset="UTF-8">
                         <style> body {{ font-family: Arial, sans-serif; padding: 20px; color: #D8000C; background-color: #FFD2D2; }} </style></head>
                         <body><h1>Error Fetching Weather Data</h1>
                         <p>Could not retrieve valid weather information. Check device logs/API config.</p></body></html>"""
                     cl.sendall(html_body.encode('utf-8')) # Send error page at once
                     print("Error response sent.")

            except OSError as e:
                 # Specifically catch errors during the send process
                 print(f"Socket Error during send: {e.args[0]} (Likely ECONNRESET - Client {client_addr} disconnected)")
                 # No need to try sending more - connection is broken
            except Exception as e:
                 print(f"Error preparing/sending response body: {e}")
                 try:
                     sys.print_exception(e)
                 except Exception: pass
                 # Don't try to send more if body generation/sending failed

        except OSError as e:
            # Errors related to accept() or other socket ops before/after send/recv
            print(f"Network/Socket Error in main loop: {e.args[0]}") # Print errno
        except Exception as e:
            print(f"An unexpected error occurred in main loop: {e}")
            try:
                sys.print_exception(e)
            except Exception: pass
        finally:
            # --- Clean up client connection ---
            if cl:
                try:
                    cl.close()
                    print(f"Client connection closed for {client_addr}.")
                except Exception as close_err:
                    print(f"Error closing client socket: {close_err}")
            # Optional: Collect garbage periodically in the main loop
            gc.collect()


# --- Main execution ---
if __name__ == "__main__":
    try:
        run_app()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"\nFatal error during execution: {e}")
        try:
            sys.print_exception(e)
        except Exception: pass
    finally:
        # Optional: Add cleanup here if needed (e.g., disable Wi-Fi)
        print("Exiting program.")
        # Maybe try disabling WLAN?
        try:
            wlan = network.WLAN(network.STA_IF)
            if wlan.isconnected():
                wlan.disconnect()
            wlan.active(False)
            print("Wi-Fi deactivated.")
        except Exception as wifi_err:
            print(f"Could not deactivate Wi-Fi: {wifi_err}")
