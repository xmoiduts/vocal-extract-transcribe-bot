#!/usr/bin/env python3
import os
import sys

def partition_wheels(wheel_dir, num_partitions):
    """
    Partitions wheel files in a directory into balanced groups based on file size.
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
    
    # Sort by size descending to help the greedy algorithm
    wheel_info.sort(key=lambda x: x['size'], reverse=True)

    partitions = [[] for _ in range(num_partitions)]
    partition_sizes = [0] * num_partitions

    for wheel in wheel_info:
        # Find the partition with the smallest current total size
        min_size_idx = min(range(num_partitions), key=lambda i: partition_sizes[i])
        
        # Add the wheel object to this partition
        partitions[min_size_idx].append(wheel)
        partition_sizes[min_size_idx] += wheel['size']

    # Create partition data with size info for sorting
    partition_data = []
    for i, partition in enumerate(partitions):
        partition_data.append({
            'index': i,
            'wheels': partition,
            'total_size': partition_sizes[i]
        })
    
    # Sort partitions by total size (ascending) so Docker layers go from small to large
    partition_data.sort(key=lambda p: p['total_size'])

    print("--- Partitioning Results ---")
    for i, data in enumerate(partition_data):
        output_filename = f'part_{i+1}_wheels.txt'

        with open(output_filename, 'w') as f:
            for wheel in data['wheels']:
                f.write(wheel['path'] + '\n')
        
        total_size_mb = data['total_size'] / (1024 * 1024)
        print(f"\nPartition {i+1} ({output_filename}): {len(data['wheels'])} wheels, Total Size: {total_size_mb:.2f} MB")
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