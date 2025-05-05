# vocal-extract-transcribe-bot
extract vocal stem of musics then transcribe and format with external big model API's

# Speed Estimation of Seperation
- GitHub Actions CPU Runner
    - Azure 4C16G?
    - `runs-on: ubuntu-latest`
    - [1/30]x | runs at 1470it/s | audio has 44100it per second
    - 10s music takes 300s to seperate.

- AWS batch fargate CPU container 1
    - AWS 4C16G container
    - [1/23]x | runs at 1900it/s | audio has 44100it per second
    - 10s music takes 23s to seperate.

- ~~AWS GPU Runner 1~~
    - ~~AWS g4dn.xlarge~~
    - AWS fargate does not support GPU yet, this issue has been open from 2019, and in mid-2025, it is still not solved.
