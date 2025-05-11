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
### - AWS g4dn.xlarge, 2x large | T4 GPU
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

## Performance Summary Table

| Platform/Instance        | CPU Config \*             | GPU Model          | Speed (it/s) | Speed Factor (x) | Time for 10s Audio (s) | Time for 3m33s Audio (s) | Time for 3m18s Audio (s) | EC2 Provisioning Time (s) \* |
|--------------------------|---------------------------|--------------------|--------------|------------------|------------------------|--------------------------|--------------------------|------------------------------|
| GitHub Actions CPU       | 4C16G ?                   |                    | 1470         | 1/30x            | 300                    |                          |                          |                              |
| AWS Fargate CPU (4C16G)  | 4C16G                     |                    | 1900         | 1/23x            | 230                    |                          |                          |                              |
| AWS Fargate CPU (16C32G) | 16C32G                    |                    | 4100         | 1/11.7x          | 110                    |                          |                          |                              |
| ~~AWS Fargate GPU~~ Fargate does not support GPU yet, this issue has been open from 2019, and in mid-2025, it is still not solved.     |  |  |  |  |  |         |                          |                              |
| Asus G14 (CPU)           | Ryzen 9 8945HS (16C32G)   |                    | 3200         | 1/13.7x          | 165                    |                          |                          |                              |
| Asus G14 (GPU)           | Ryzen 9 8945HS (16C32G)   | RTX 4060 Laptop    | 100000 \*    | 2.26x            |                        |                          |                          |                              |
| AWS g4dn.xlarge          | 4C15G                     | T4                 | 102700       | 2.33x            | 4.3                    | 95                       | 88                       |                              |
| AWS g4dn.2xlarge         | 8C30G                     | T4                 | 102100       | 2.33x            | 4.3                    | 98                       | 89                       |                              |
| AWS g5.2xlarge           | 8C30G                     | A10G               | 208500       | 4.5x             |                        | 49                       | 43                       | 170                          |
| AWS g5.xlarge            | 4C15G                     | A10G               | 209000       | 4.5x             |                        | 46                       | 43                       |                              |
| AWS g6.2xlarge           | 8C30G                     | L4                 | 135600       | 3.05x            |                        | 71                       | 67                       |                              |
| AWS g6.xlarge            | 4C15G                     | L4                 | 130000       | 2.95x            |                        | 73                       | 69                       |                              |
| AWS g6e.2xlarge          | 8C30G                     | L40s               | 428500       | 9.7x             |                        | 23                       | 21                       | 280                          |
| AWS g6e.xlarge           | 4C15G                     | L40s               | 426500       | 9.7x             |                        | 23                       | 21                       |                              |

### Note:
- VM, physical machine, and serverless container tasks (GitHub Actions, AWS Fargate) record the total CPU and memory that the task can access;
- We reserve 1GB memory for host VM for AWS Batch EC2 container tasks to avoid instance boot failure on exact CPU instances. (i.e. if we have 4c16g instance and we try to land 4c16g container onto it then it might fail)
- For our usage, 4 CPU cores will be enough for T4, A10G, L4 and L40s GPU whereas we thought CPU was also a bottleneck for GPU tasks.
- Our usage: `model_bs_roformer_ep_368_sdr_12.9628.yaml` to process mp3 audio.
- The 3-min test mp3's are 128kbps 44100Hz.
- EC2 boot time is defined as the time offset between instance launch time and job start time.
- The upper table is tested under a 10GB docker storaged on Github Packages then pulls to AWS.
- Audio is 44100it/s; 48khz audio on AWS GPU will crash but works on Asus G14.
- Asus ROG G14 runs at 96000it/s under windows performance mode and 100000it/s under windows power efficiency mode.
    - Possibly because efficiency mode restricts CPU Energy Performance Preference (EPP), resulting in reduced frequency and power consumption, allowing more power allocation to the GPU.