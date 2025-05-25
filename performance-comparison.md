# Speed Estimation of Seperation

Exclude setup and teardown time, pure inference speed.
Using model: `model_bs_roformer_ep_368_sdr_12.9628.yaml`

## GitHub Actions CPU Runner 4C16G?
- Azure 4C16G?
- `runs-on: ubuntu-latest`
- [1/30]x | runs at 1470it/s | audio has 44100it per second
- 10s music takes 300s to seperate.

## AWS batch fargate CPU container 4C16G
- AWS 4C16G container
- [1/23]x | runs at 1900it/s | audio has 44100it per second
- 10s music takes 230s to seperate.
- 4C8G-1270it/s
- 4C16G-1700it/s

## AWS batch fargate CPU container 16C32G
- AWS 16C32G container
- [1/11.7]x | runs at 4100it/s | audio has 44100it per second
- 10s music takes 110s to seperate.

## ~~AWS GPU Runner 4C16G-NV-T4-GPU~~
- ~~AWS g4dn.xlarge~~
- AWS fargate does not support GPU yet, this issue has been open from 2019, and in mid-2025, it is still not solved.

## Asus ROG Zephyrus G14 air 2024 CPU
- AMD Ryzen 9 8945HS 16C32G
- No containerization, just run the script directly in python virtual environment.
- [1/13.7]x | runs at 3200it/s | audio has 44100it per second
- 10s music takes 165s to seperate.

## Asus ROG Zephyrus G14 air 2024 GPU
- AMD Ryzen 9 8945HS 16C32G
- Nvidia RTX 4060 Laptop GPU
- 2.26x | runs at 100000it/s | Windows power efficiency mode | audio has 44100it per second
- 96000it/s | windows performance mode
- possibly because efficiency mode restricts CPU Energy Performance Preference (EPP), resulting in reduced frequency and power consumption, allowing more power allocation to the GPU

## AWS Batch EC2 GPU containers
### AWS g4dn.xlarge, 2x large | T4 GPU
- xlarge = 4C16G, 2xlarge = 8C32G
- [2.33]x | runs at 103000it/s | audio has 44100it per second
- 10s music takes 4.3s to seperate.

### AWS g5.2xlarge | A10G GPU
- EC2 provitions in 170s
- 2xlarge = 8C32G
- [4.5]x | runs at 208500it/s | audio has 44100it per second
- 3:33 music takes 49s
- 3:18 music takes 43s

### AWS g5.xlarge | A10G GPU
- xlarge = 4C16G
- [4.5]x | runs at 209000it/s | audio has 44100it per second
- 3:33 music takes 46s
- 3:18 music takes 43s

### AWS g6.2xlarge | L4 GPU
- 2xlarge = 8C32G
- [3.05]x | runs at 135600it/s | audio has 44100it per second
- 3:33 music takes 71s
- 3:18 music takes 67s
- Note: 4c15g / 8c30g containers running on g6.2xlarge EC2 instance have nearly the same speed.


### AWS g6.xlarge | L4 GPU
- xlarge = 4C16G
- [2.95]x | runs at 130000it/s | audio has 44100it per second
- 3:33 music takes 73s
- 3:18 music takes 69s

### AWS g6e.2xlarge | L40s GPU
- EC2 provitions in 280s
- 2xlarge = 8C64G
- [9.7]x | runs at 428500it/s | audio has 44100it per second
- 3:33 music takes 23s
- 3:18 music takes 21s

## RunPod Serverless
### RTX A4000 10C20G EPYC
- US-IL-1
- Container starts in 130s
- [4.03]x | runs at 178000it/s | audio has 44100it per second
- 3:33 music takes 53s
- 3:18 music takes 49s
- "RTX4000 Ada" performance is on par with "RTX4000"

### RTX A4500 12C62G Epyc 7352
- EU-RO-1
- Container starts in 105s
- [5.55]x | runs at 245000it/s | audio has 44100it per second
- 3:33 music takes 39s
- 3:18 music takes 36s

### RTX 2000 Ada 6C31G
- EU-RO-1
- Container starts in 5s
- [2.42]x | runs at 107000it/s | audio has 44100it per second
- 3:33 music takes 89s
- 3:18 music takes 84s

### RTX A5000 9C50G
- CA-MTL-1
- Container starts in 10s
- [6.4]x | runs at 285000it/s | audio has 44100it per second
- 3:33 music takes 34s
- 3:18 music takes 31s

### CA-MTL-1 A40 9 vCPUs 50 GB RAM
- Container starts in 4s
- [6.23]x | runs at 275000it/s | audio has 44100it per second
- 3:33 music takes 35s
- 3:18 music takes 33s

### US-KS-2 L40 32c 250GB RAM
- up in 6s
- [7.65]x | runs at 337500it/s | audio has 44100it per second
- 3:33 music takes 29s
- 3:18 music takes 26s


### L4 14C55G EPYC 7702
- EUR-IS-1
- Container starts in 18s
- [3.04]x | runs at 134500it/s | audio has 44100it per second
- 3:33 music takes 72s
- 3:18 music takes 67s

### L40S 16c94g
- OC-AU-1
- Container starts in 9s
- [9.75]x | runs at 430000it/s | audio has 44100it per second
- 3:33 music takes 22s
- 3:18 music takes 20s


### H100 SXM 28c 251g intel xeon platinium 8570
- cached, no container start time
- [21.7]x | 957000it/s
- 3:33 music takes 10s
- 3:18 music takes 9s

# Performance Summary Table

| Platform/Instance        | CPU Config \*             | GPU Model          | Speed (it/s) | Speed Factor (x) | Time for 10s Audio (s) | Time for 3m33s Audio (s) | Time for 3m18s Audio (s) | EC2 Provisioning Time (s) \* | Price per Sec (USD)   | Cost-Effectiveness (Factor/Price/s) |
|--------------------------|---------------------------|--------------------|--------------|------------------|------------------------|--------------------------|--------------------------|------------------------------|-----------------------|-------------------------------------|
| GitHub Actions CPU       | 4C16G ?                   |                    | 1470         | 1/30x            | 300                    |                          |                          |                              | N/A                   | N/A                                 |
| AWS Fargate CPU (4C16G)  | 4C16G                     |                    | 1900         | 1/23x            | 230                    |                          |                          |                              | N/A                   | N/A                                 |
| AWS Fargate CPU (16C32G) | 16C32G                    |                    | 4100         | 1/11.7x          | 110                    |                          |                          |                              | N/A                   | N/A                                 |
| ~~AWS Fargate GPU~~ Fargate does not support GPU yet, this issue has been open from 2019, and in mid-2025, it is still not solved.     |  |  |  |  |  |         |                          |                              | N/A                   | N/A                                 |
| Asus G14 (CPU)           | Ryzen 9 8945HS (16C32G)   |                    | 3200         | 1/13.7x          | 165                    |                          |                          |                              | N/A                   | N/A                                 |
| Asus G14 (GPU)           | Ryzen 9 8945HS (16C32G)   | RTX 4060 Laptop    | 100000 \*    | 2.26x            |                        |                          |                          |                              | N/A                   | N/A                                 |
| AWS g4dn.xlarge          | 4C15G                     | T4                 | 102700       | 2.33x            | 4.3                    | 95                       | 88                       |                              | N/A                   | N/A                                 |
| AWS g4dn.2xlarge         | 8C30G                     | T4                 | 102100       | 2.33x            | 4.3                    | 98                       | 89                       |                              | N/A                   | N/A                                 |
| AWS g5.2xlarge           | 8C30G                     | A10G               | 208500       | 4.5x             |                        | 49                       | 43                       | 170                          | N/A                   | N/A                                 |
| AWS g5.xlarge            | 4C15G                     | A10G               | 209000       | 4.5x             |                        | 46                       | 43                       |                              | N/A                   | N/A                                 |
| AWS g6.2xlarge           | 8C30G                     | L4                 | 135600       | 3.05x            |                        | 71                       | 67                       |                              | N/A                   | N/A                                 |
| AWS g6.xlarge            | 4C15G                     | L4                 | 130000       | 2.95x            |                        | 73                       | 69                       |                              | N/A                   | N/A                                 |
| AWS g6e.2xlarge          | 8C30G                     | L40s               | 428500       | 9.7x             |                        | 23                       | 21                       | 280                          | N/A                   | N/A                                 |
| AWS g6e.xlarge           | 4C15G                     | L40s               | 426500       | 9.7x             |                        | 23                       | 21                       |                              | N/A                   | N/A                                 |
| RunPod RTX A4000         | 10C20G EPYC               | RTX A4000          | 178000       | 4.03x            |                        | 53                       | 49                       | 130 (Container Start)        | 0.00016               | 25188                               |
| RunPod RTX A4500         | 12C62G EPYC 7352          | RTX A4500          | 245000       | 5.55x            |                        | 39                       | 36                       | 105 (Container Start)        | 0.00016               | 34688                               |
| RunPod RTX 2000 Ada      | 6C31G                     | RTX 2000 Ada       | 107000       | 2.42x            |                        | 89                       | 84                       | 5 (Container Start)          | 0.00016               | 15125                               |
| RunPod RTX A5000         | 9C50G                     | RTX A5000          | 285000       | 6.4x             |                        | 34                       | 31                       | 10 (Container Start)         | 0.00019               | 33684                               |
| RunPod A40               | 9C50G                     | A40                | 275000       | 6.23x            |                        | 35                       | 33                       | 4 (Container Start)          | 0.00034               | 18324                               |
| RunPod L40               | 32C250G                   | L40                | 337500       | 7.65x            |                        | 29                       | 26                       | 6 (Container Start)          | 0.00053               | 14434                               |
| RunPod L40S              | 16C94G                    | L40S               | 430000       | 9.75x            |                        | 22                       | 20                       | 9 (Container Start)          | 0.00053               | 18396                               |
| RunPod L4                | 14C55G EPYC 7702          | L4                 | 134500       | 3.04x            |                        | 72                       | 67                       | 18 (Container Start)         | 0.00019               | 16000                               |
| RunPod H100 SXM          | 28C251G Xeon 8570         | H100 SXM           | 957000       | 21.7x            |                        | 10                       | 9                        | 0 (cached)                   | 0.00116               | 18707                               |

## Note:
### workload characteristics
- Our usage: `model_bs_roformer_ep_368_sdr_12.9628.yaml` to process mp3 audio.
- For our usage, 4 CPU cores will be enough for T4, A10G, L4 and L40s GPU whereas we thought CPU was also a bottleneck for GPU tasks.
- The 3-min test mp3's are 128kbps 44100Hz.
- Every second of 44.1khz audio takes 44100[it]'s to inference.
- Multiple GPU's on one container/node won't speed up the inference, MSST uses only one.
- The model on Runpod telemetry takes 2.2GB VRAM.
### Flavor
- VM, physical machine, and serverless container tasks (GitHub Actions, AWS Fargate) record the total CPU and memory that the task can access, runpod tasks record workers' telemetry claims;
- We reserve 1GB memory for host VM for AWS Batch EC2 container tasks to avoid instance boot failure on exact CPU instances. (i.e. if we have 4c16g instance and we try to land 4c16g container onto it then it might fail)
### overhead
- EC2 boot time is defined as the time offset between instance launch time and job start time.
- Some AWS tasks are tested with a 4-5GB (compressed) Github docker Packages pulled to AWS
    - RunPod serverless tasks always pre-pull docker images before being triggered.
- cost effectiveness calculation accounts for pure inference time, overhead time is not included.
### Device differences
- 48khz audio on AWS GPU will crash but works on Asus G14.
- Asus ROG G14 runs at 96000it/s under windows performance mode and 100000it/s under windows power efficiency mode.
    - Possibly because efficiency mode restricts CPU Energy Performance Preference (EPP), resulting in reduced frequency and power consumption, allowing more power allocation to the GPU.
- RunPod 3090 4090 5090 serverless workers (home GPU) cannot launch this container.
