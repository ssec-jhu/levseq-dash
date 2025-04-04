import os
import random
import re
import string

import pandas as pd

# Define constants
WELLS = [f"{row}{col}" for row in "ABCDEFGH" for col in range(1, 13)]
NUCLEOTIDES = ["A", "C", "G", "T"]
CODON_TABLE = {
    "ATA": "I",
    "ATC": "I",
    "ATT": "I",
    "ATG": "M",
    "ACA": "T",
    "ACC": "T",
    "ACG": "T",
    "ACT": "T",
    "AAC": "N",
    "AAT": "N",
    "AAA": "K",
    "AAG": "K",
    "AGC": "S",
    "AGT": "S",
    "AGA": "R",
    "AGG": "R",
    "CTA": "L",
    "CTC": "L",
    "CTG": "L",
    "CTT": "L",
    "CCA": "P",
    "CCC": "P",
    "CCG": "P",
    "CCT": "P",
    "CAC": "H",
    "CAT": "H",
    "CAA": "Q",
    "CAG": "Q",
    "CGA": "R",
    "CGC": "R",
    "CGG": "R",
    "CGT": "R",
    "GTA": "V",
    "GTC": "V",
    "GTG": "V",
    "GTT": "V",
    "GCA": "A",
    "GCC": "A",
    "GCG": "A",
    "GCT": "A",
    "GAC": "D",
    "GAT": "D",
    "GAA": "E",
    "GAG": "E",
    "GGA": "G",
    "GGC": "G",
    "GGG": "G",
    "GGT": "G",
    "TCA": "S",
    "TCC": "S",
    "TCG": "S",
    "TCT": "S",
    "TTC": "F",
    "TTT": "F",
    "TTA": "L",
    "TTG": "L",
    "TAC": "Y",
    "TAT": "Y",
    "TAA": "*",
    "TAG": "*",
    "TGC": "C",
    "TGT": "C",
    "TGA": "*",
    "TGG": "W",
}


def generate_random_dna(length=300):
    """Generate a random DNA sequence of given length"""
    return "".join(random.choice(NUCLEOTIDES) for _ in range(length))


def mutate_dna(dna_sequence, num_mutations):
    """Introduce random mutations in the DNA sequence with chance of indels"""
    # If no mutations, return the original sequence and mark as PARENT
    if num_mutations == 0:
        return dna_sequence, "#PARENT#"

    dna_list = list(dna_sequence)
    sequence_length = len(dna_list)

    # Store positions and changes for tracking mutations
    mutations = []
    has_indel = False

    for _ in range(num_mutations):
        # Check for insertion or deletion (0.1% chance) - increased from 0.01%
        indel_chance = random.random() <= 0.001  # 0.1%

        if indel_chance:
            has_indel = True
            indel_type = random.choice(["insertion", "deletion"])

            # Select a random position
            pos = random.randint(0, sequence_length - 1)

            if indel_type == "insertion":
                # Insert a random nucleotide
                new_nucleotide = random.choice(NUCLEOTIDES)
                dna_list.insert(pos, new_nucleotide)
                sequence_length += 1
                mutations.append(f"ins{pos + 1}{new_nucleotide}")
            else:  # deletion
                # Delete a nucleotide
                deleted = dna_list.pop(pos)
                sequence_length -= 1
                mutations.append(f"del{pos + 1}{deleted}")
        else:
            # Regular substitution mutation
            pos = random.randint(0, sequence_length - 1)
            original = dna_list[pos]
            choices = [n for n in NUCLEOTIDES if n != original]
            new_nucleotide = random.choice(choices)
            dna_list[pos] = new_nucleotide
            mutations.append(f"{original}{pos + 1}{new_nucleotide}")

    # Sort mutations by position number
    def get_position(mutation_string):
        # Extract position number using regex
        match = re.search(r"[A-Za-z]+(\d+)[A-Za-z]+", mutation_string)
        if match:
            return int(match.group(1))
        return 0

    mutations.sort(key=get_position)

    # Form the mutation string with underscores
    if has_indel:
        return "".join(dna_list), "#INS#" if "ins" in "_".join(mutations) else "#DEL#"
    else:
        return "".join(dna_list), "_".join(mutations)


def translate_dna_to_protein(dna_sequence):
    """Translate DNA sequence to protein sequence using the standard genetic code"""
    protein = []
    for i in range(0, len(dna_sequence), 3):
        if i + 3 <= len(dna_sequence):
            codon = dna_sequence[i : i + 3]
            amino_acid = CODON_TABLE.get(codon, "X")  # 'X' for unknown codons
            protein.append(amino_acid)

    return "".join(protein)


def compare_proteins(parent_protein, mutant_protein):
    """Compare two protein sequences and identify substitutions"""
    # If proteins are identical, mark as PARENT
    if parent_protein == mutant_protein:
        return "#PARENT#"

    substitutions = []

    # Check for length differences - might indicate frameshift from indel
    if len(parent_protein) != len(mutant_protein):
        # Check if mutant is shorter (could be deletion)
        if len(parent_protein) > len(mutant_protein):
            return "#DEL#"
        else:
            return "#INS#"

    # Check for substitutions
    for i in range(min(len(parent_protein), len(mutant_protein))):
        if parent_protein[i] != mutant_protein[i]:
            substitutions.append(f"{parent_protein[i]}{i + 1}{mutant_protein[i]}")

    # Sort substitutions by position number
    def get_position(sub_string):
        match = re.search(r"[A-Za-z](\d+)[A-Za-z]", sub_string)
        if match:
            return int(match.group(1))
        return 0

    substitutions.sort(key=get_position)

    return "_".join(substitutions)


def generate_plate_name():
    """Generate a random plate name"""
    prefix = "".join(random.choice(string.ascii_uppercase) for _ in range(2))
    suffix = "".join(random.choice(string.digits) for _ in range(3))
    return f"{prefix}-{suffix}"


def generate_dataset(parent_dna, num_plates, cas_numbers, fitness_min, fitness_max, parents_per_plate):
    """Generate the complete dataset based on input parameters"""
    data = []

    # Translate parent DNA to protein
    parent_protein = translate_dna_to_protein(parent_dna)

    # Generate plate names and barcode values
    plate_info = {}
    for i in range(1, num_plates + 1):
        barcode_plate = random.randint(1, 96)
        plate_name = generate_plate_name()
        plate_info[i] = {"barcode_plate": barcode_plate, "plate_name": plate_name}

    # Dictionary to track sequences and their fitness values for consistency
    sequence_fitness = {}

    # Generate base fitness values for parent sequence per CAS number
    parent_fitness = {}
    for cas_number in cas_numbers:
        # Use user-specified fitness range for parent sequences
        parent_baseline = (fitness_min + fitness_max) / 2
        parent_range = (fitness_max - fitness_min) * 0.2  # 20% of the range
        parent_fitness[cas_number] = random.uniform(
            max(fitness_min, parent_baseline - parent_range), min(fitness_max, parent_baseline + parent_range)
        )

    # For each plate, generate data for all wells and all CAS numbers
    for plate_num in range(1, num_plates + 1):
        plate_name = plate_info[plate_num]["plate_name"]
        barcode_plate = plate_info[plate_num]["barcode_plate"]

        # Randomly select wells for parent sequences
        parent_wells = random.sample(WELLS, min(parents_per_plate, len(WELLS)))

        for well in WELLS:
            # Decide number of mutations - 0 for parent wells, 1-15 for others
            if well in parent_wells:
                num_mutations = 0  # Parent sequence
            else:
                num_mutations = random.randint(1, 15)  # Ensure at least 1 mutation for non-parents

            # Mutate DNA and get mutation notation
            mutated_dna, nucleotide_mutation = mutate_dna(parent_dna, num_mutations)

            # Translate to protein
            mutated_protein = translate_dna_to_protein(mutated_dna)

            # Get amino acid substitutions
            amino_acid_substitutions = compare_proteins(parent_protein, mutated_protein)

            # Generate random alignment count
            alignment_count = random.randint(1, 1000)

            # Check if we need to mark as LOW
            if alignment_count < 10:
                amino_acid_substitutions = "#LOW#"

            # Generate alignment probability
            alignment_probability = random.uniform(0.7, 1.0)

            # Generate coordinates
            x_coordinate = random.uniform(0, 100)
            y_coordinate = random.uniform(0, 100)

            # Create ID
            id_value = f"{plate_name}-{well}"

            # Create a sequence key for tracking similar sequences
            sequence_key = f"{mutated_dna}_{nucleotide_mutation}_{amino_acid_substitutions}"

            # Add an entry for each CAS number
            for cas_number in cas_numbers:
                # Determine fitness value based on sequence
                if sequence_key in sequence_fitness and cas_number in sequence_fitness[sequence_key]:
                    # Use previously assigned fitness value for this sequence/CAS
                    fitness_value = sequence_fitness[sequence_key][cas_number]
                    # Add small random variation (±1%)
                    fitness_value *= random.uniform(0.99, 1.01)
                else:
                    # Generate new fitness value
                    if amino_acid_substitutions == "#PARENT#":
                        # Parent variants have similar values with small variations
                        fitness_value = parent_fitness[cas_number] * random.uniform(0.95, 1.05)
                    else:
                        # Mutants have values that might differ more significantly
                        base_value = random.uniform(fitness_min, fitness_max)
                        # Different CAS numbers can affect the fitness differently
                        cas_factor = random.uniform(0.7, 1.3)
                        # Keep within the specified range
                        fitness_value = min(max(base_value * cas_factor, fitness_min), fitness_max)

                    # Store for future reference
                    if sequence_key not in sequence_fitness:
                        sequence_fitness[sequence_key] = {}
                    sequence_fitness[sequence_key][cas_number] = fitness_value

                # Create data row
                row = {
                    "id": id_value,
                    "barcode_plate": barcode_plate,
                    "cas_number": cas_number,
                    "plate": plate_name,
                    "well": well,
                    "alignment_count": alignment_count,
                    "nucleotide_mutation": nucleotide_mutation,
                    "amino_acid_substitutions": amino_acid_substitutions,
                    "alignment_probability": round(alignment_probability, 4),
                    "nt_sequence": mutated_dna,
                    "aa_sequence": mutated_protein,
                    "x_coordinate": round(x_coordinate, 4),
                    "y_coordinate": round(y_coordinate, 4),
                    "fitness_value": round(fitness_value, 2),
                }

                data.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df


def validate_dna_sequence(sequence):
    """Validate that a string is a valid DNA sequence"""
    valid_nucleotides = set(NUCLEOTIDES)
    return all(nucleotide in valid_nucleotides for nucleotide in sequence.upper())


def main():
    print("DNA Mutation and Protein Translation Simulator")
    print("-" * 50)

    # Get input parameters from the user
    cas_input = input("Enter CAS number(s), separated by commas: ")
    cas_numbers = [cas.strip() for cas in cas_input.split(",")]

    while True:
        try:
            num_plates = int(input("Enter the number of plates to generate: "))
            if num_plates <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    # Get number of parent sequences per plate
    while True:
        try:
            parents_per_plate = int(input("Enter number of parent sequences per plate (default: 3): ") or "3")
            if parents_per_plate < 0:
                print("Please enter a non-negative number.")
                continue
            if parents_per_plate > 96:
                print("A plate can have at most 96 wells.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    # Get parent DNA sequence from user or generate randomly
    use_custom = input("Do you want to input a parent DNA sequence? (y/n): ").lower()

    if use_custom == "y":
        while True:
            parent_dna = input("Enter parent DNA sequence (A, C, G, T only): ").upper()
            if validate_dna_sequence(parent_dna):
                break
            else:
                print("Invalid DNA sequence. Please use only A, C, G, T nucleotides.")
    else:
        parent_dna_length = int(input("Enter length for random parent DNA sequence: ") or "300")
        parent_dna = generate_random_dna(parent_dna_length)
        print(f"Generated parent DNA sequence: {parent_dna}")

    # Get fitness value range from user
    while True:
        try:
            fitness_min = float(input("Enter minimum fitness value (default: 500): ") or "500")
            fitness_max = float(input("Enter maximum fitness value (default: 5000): ") or "5000")

            if fitness_min >= fitness_max:
                print("Minimum fitness must be less than maximum fitness.")
                continue

            if fitness_min < 0:
                print("Fitness values should be positive.")
                continue

            break
        except ValueError:
            print("Please enter valid numbers for fitness range.")

    # Get output filename from user
    default_filename = "mutation_dataset.csv"
    output_file = input(f"Enter output filename (default: {default_filename}): ")

    # Use default if no input
    if not output_file:
        output_file = default_filename

    # Add .csv extension if not present
    if not output_file.lower().endswith(".csv"):
        output_file += ".csv"

    print("\nGenerating dataset...")
    df = generate_dataset(parent_dna, num_plates, cas_numbers, fitness_min, fitness_max, parents_per_plate)

    # Save to CSV
    df.to_csv(output_file, index=False)

    # Get full path to output file
    full_path = os.path.abspath(output_file)

    print(f"\nDataset generated successfully and saved to {full_path}")
    print(f"Total records: {len(df)}")
    print(f"Parent DNA sequence: {parent_dna}")
    print(f"Parent protein sequence: {translate_dna_to_protein(parent_dna)}")
    print(f"Fitness value range: {fitness_min} to {fitness_max}")
    print(f"Parents per plate: {parents_per_plate}")


if __name__ == "__main__":
    main()
