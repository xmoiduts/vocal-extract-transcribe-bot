#!/usr/bin/env python3
import os
import sys

def partition_wheels(wheel_dir, num_partitions):
    """
    Partitions wheel files in a directory into optimized groups for Docker layer downloading.
    Creates intentionally uneven partitions to maximize parallel download/extract efficiency.
    """
    try:
        # Use absolute paths for items in wheel_dir
        wheel_files = [os.path.join(wheel_dir, f) for f in os.listdir(wheel_dir) if f.endswith('.whl')]
    except FileNotFoundError:
        print(f"Error: Directory not found at {wheel_dir}", file=sys.stderr)
        sys.exit(1)

    wheel_info = []
    for fpath in wheel_files:
        try:
            size = os.path.getsize(fpath)
            wheel_info.append({'path': fpath, 'size': size})
        except FileNotFoundError:
            print(f"Warning: Could not get size of {fpath}, skipping.", file=sys.stderr)
            continue
    
    # Sort by size descending to help the algorithm
    wheel_info.sort(key=lambda x: x['size'], reverse=True)

    # Calculate total size for intelligent partitioning
    total_size = sum(wheel['size'] for wheel in wheel_info)
    
    # Create target sizes: smallest = max * 0.5, others distributed proportionally
    # Strategy: smallest partition gets priority download, others increase gradually
    target_ratios = []
    if num_partitions >= 2:
        # Calculate ratios so that smallest is 0.5 of the largest
        # If largest = L, smallest = 0.5*L, and sum = 1.0
        # Let's set largest = 2*smallest, and distribute others linearly
        
        # For linear distribution: smallest, ..., largest where largest = 2*smallest
        # Sum = smallest * (1 + k2 + k3 + ... + 2) where ki are multipliers
        # For even distribution: ki = 1 + (i-1) * (2-1)/(n-1) = 1 + (i-1)/(n-1)
        multipliers = []
        for i in range(num_partitions):
            multiplier = 1.0 + i * 1.0 / (num_partitions - 1)  # 1.0 to 2.0
            multipliers.append(multiplier)
        
        # Calculate smallest ratio so that sum equals 1.0
        total_multiplier = sum(multipliers)
        smallest_ratio = 1.0 / total_multiplier
        
        target_ratios = [smallest_ratio * m for m in multipliers]
    else:
        target_ratios = [1.0]
    
    target_sizes = [int(total_size * ratio) for ratio in target_ratios]
    
    print(f"Target partition ratios: {[f'{r:.2%}' for r in target_ratios]}")
    print(f"Target sizes (MB): {[f'{s/(1024*1024):.1f}' for s in target_sizes]}")
    
    # Initialize partitions
    partitions = [[] for _ in range(num_partitions)]
    partition_sizes = [0] * num_partitions
    
    # Assign wheels to partitions to match target sizes
    for wheel in wheel_info:
        # Find the partition that needs this wheel most (furthest from target)
        best_partition = 0
        best_score = float('inf')
        
        for i in range(num_partitions):
            # Calculate how much over/under target this partition would be
            new_size = partition_sizes[i] + wheel['size']
            target_diff = abs(new_size - target_sizes[i])
            
            # Prefer partitions that are under their target
            if partition_sizes[i] < target_sizes[i]:
                score = target_diff
            else:
                score = target_diff + total_size  # Penalty for exceeding target
            
            if score < best_score:
                best_score = score
                best_partition = i
        
        partitions[best_partition].append(wheel)
        partition_sizes[best_partition] += wheel['size']

    # Create partition data with size info for sorting
    partition_data = []
    for i, partition in enumerate(partitions):
        partition_data.append({
            'index': i,
            'wheels': partition,
            'total_size': partition_sizes[i]
        })
    
    # Sort partitions: smallest first (for priority download), then ascending by size
    # This allows smallest layer to download first and start extracting while others download
    partition_data.sort(key=lambda p: p['total_size'])

    print("--- Partitioning Results ---")
    
    # Calculate and display size ratios
    smallest_size = partition_data[0]['total_size']
    largest_size = partition_data[-1]['total_size']
    ratio = smallest_size / largest_size if largest_size > 0 else 0
    
    print(f"Smallest partition size: {smallest_size/(1024*1024):.1f} MB")
    print(f"Largest partition size: {largest_size/(1024*1024):.1f} MB") 
    print(f"Size ratio (smallest/largest): {ratio:.2f} (target: ~0.50)")
    print(f"Download order: smallest first, then ascending by size")
    print()
    
    for i, data in enumerate(partition_data):
        output_filename = f'part_{i+1}_wheels.txt'

        with open(output_filename, 'w') as f:
            for wheel in data['wheels']:
                f.write(wheel['path'] + '\n')
        
        total_size_mb = data['total_size'] / (1024 * 1024)
        priority_note = " (PRIORITY DOWNLOAD)" if i == 0 else ""
        print(f"Partition {i+1} ({output_filename}): {len(data['wheels'])} wheels, Total Size: {total_size_mb:.2f} MB{priority_note}")
        # Print wheels in the partition
        for wheel in data['wheels']:
            print(f"  - {os.path.basename(wheel['path'])}")
    print("\n--------------------------")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <wheel_directory> <num_partitions>", file=sys.stderr)
        sys.exit(1)
    
    wheel_dir_path = sys.argv[1]
    num_parts = int(sys.argv[2])
    partition_wheels(wheel_dir_path, num_parts) 