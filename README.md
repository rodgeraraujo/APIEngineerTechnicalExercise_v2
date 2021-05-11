# APIEngineerTechnicalExercise
Python Script that converts Airplane Seatmap XML, into readable JSON file.

## Usage
- Run `seatmap_parser.py` with a XML Filename as the argument (correspond to the file formats of [seatmap1.xml](seatmap1.xml))
- After script running, a new JSON file with the "`filename`_parsed" will be created in the same directory

```
python seatmap_parser.py [FILENAME]

```
Output
> python3 seatmap_parser.py seatmap1.xml
`JSON result created of 'seatmap1.xml' in new file 'seatmap1_parsed.json'`
