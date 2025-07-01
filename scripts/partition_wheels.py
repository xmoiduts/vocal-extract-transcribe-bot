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
        
        # Add the wheel to this partition
        partitions[min_size_idx].append(wheel['path'])
        partition_sizes[min_size_idx] += wheel['size']

    print("--- Partitioning Results ---")
    for i, partition in enumerate(partitions):
        output_filename = f'part_{i+1}_wheels.txt'
        with open(output_filename, 'w') as f:
            # Sort for determinism, though not strictly necessary
            for path in sorted(partition):
                f.write(path + '\n')
        
        total_size_mb = partition_sizes[i] / (1024 * 1024)
        print(f"Partition {i+1} ({output_filename}): {len(partition)} wheels, Total Size: {total_size_mb:.2f} MB")
    print("--------------------------")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <wheel_directory> <num_partitions>", file=sys.stderr)
        sys.exit(1)
    
    wheel_dir_path = sys.argv[1]
    num_parts = int(sys.argv[2])
    partition_wheels(wheel_dir_path, num_parts) 