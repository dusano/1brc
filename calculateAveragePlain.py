import sys
from typing import Dict, Tuple
import io

def read_measurements(filename: str) -> Dict[str, Tuple[float, float, int, float]]:
    measurements: Dict[str, Tuple[float, float, int, float]] = {}
    try:
        with open(filename, 'r', encoding='utf-8', buffering=1024*1024) as file:
            buffer = io.StringIO(file.read())
            for line_number, line in enumerate(buffer, 1):
                station, temp_str = line.rstrip().split(';')
                station = sys.intern(station)
                if not station or len(station.encode('utf-8')) > 100:
                    print(f"Error parsing line {line_number}: Invalid station name: {station}", file=sys.stderr)
                    continue
                try:
                    temp = float(temp_str)
                except ValueError:
                    print(f"Error parsing line {line_number}: Invalid temperature value: {temp_str}", file=sys.stderr)
                    continue
                if not -99.9 <= temp <= 99.9 or len(temp_str.split('.')[1]) != 1:
                    print(f"Error parsing line {line_number}: Temperature out of range or invalid format: {temp_str}", file=sys.stderr)
                    continue
                if station in measurements:
                    min_temp, sum_temp, count, max_temp = measurements[station]
                    measurements[station] = (min(min_temp, temp), sum_temp + temp, count + 1, max(max_temp, temp))
                else:
                    measurements[station] = (temp, temp, 1, temp)
    except IOError as e:
        print(f"Error reading file {filename}: {e}", file=sys.stderr)
        sys.exit(1)
    
    if len(measurements) > 10000:
        print(f"Warning: More than 10,000 unique station names found ({len(measurements)})", file=sys.stderr)

    return measurements

def format_output(measurements: Dict[str, Tuple[float, float, int, float]]) -> str:
    output = ["{"]
    for station in sorted(measurements):
        min_temp, sum_temp, count, max_temp = measurements[station]
        mean_temp = sum_temp / count
        output.append(f"{station}={min_temp:.1f}/{mean_temp:.1f}/{max_temp:.1f}, ")
    output.append("\b\b}")
    return "".join(output) + " "

def main():
    if len(sys.argv) != 2:
        print("Usage: python calculateAveragePlain.py <measurements_file>", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]
    measurements = read_measurements(filename)
    output = format_output(measurements)
    print(output)

if __name__ == "__main__":
    main()