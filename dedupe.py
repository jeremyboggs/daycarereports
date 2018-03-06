with open('inspections.csv','r') as file_in, open('inspections_dedupe.csv','w') as file_out:
    seen = set()
    for line in file_in:
        if line in seen: continue

        seen.add(line)
        file_out.write(line)

