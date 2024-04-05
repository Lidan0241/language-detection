# Extraction de data test de ASCEND - transcription des audios en-zh
import csv

file_path = 'test_metadata.csv'  # Remplacez avec le chemin de votre fichier
output_file = 'extracted_transcriptions.txt'  # Nom du fichier de sortie

with open(file_path, newline='', encoding='utf-8') as csvfile, open(output_file, 'w', encoding='utf-8') as txtfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        txtfile.write(row['transcription'] + '\n')

print(f"Transcriptions enregistrées dans {output_file}")
