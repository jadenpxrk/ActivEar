# HackTheNorth2023

![activ](https://github.com/JaehyeongPark06/ActivEar/assets/78674944/0d4b7142-6b34-45eb-8591-3afb3818ab1c)

## Live Demo
[Link](https://devpost.com/software/alzheimear)

## Inspiration

As a team, we collectively understand the struggles of being forgetful. With needing to remake an Apple ID password on every login, it gets frustrating, and that’s only a fraction of what patients with Alzheimer's experience. With this in mind, we built ActivEar.

## What it does

ActivEar is an application that continuously records, transfers, and transcribes data from the user. Utilizing the microphone, it transforms audio into text that is then stored in a vector database. When the user asks a question, ActivEar retrieves and searches the relevant data, using an API to provide helpful answers.

## How we built it

Originally, we had planned for a major hardware component that consisted of an ESP32-based microcontroller, a microphone, a speaker, and a battery. The goal was to have an inexpensive, portable method of access to ActivEar's services. Unfortunately, we ran across multiple unrecoverable issues. After we had tested each component and subsequently soldered the circuit together, we discovered a short that proved fatal to the microcontroller. Despite this, we carried on and loaned an alternative microcontroller. After a minor redesign and reassembly, we later discovered that some of the crucial libraries we had been using were no longer compatible and there were no functional equivalents. Defeated, sleep-deprived, and with 9 hours remaining, we went back to the drawing board to see how we could salvage what we had. Most of the software backend had been completed at this point, so we made the difficult decision of dropping the hardware component completely in favour of a multi-platform application. With only 8 hours remaining, we successfully put together a working browser demo as shown.

## Challenges we ran into

Despite facing so many challenges, we never gave up and continued to work past them. We learned the importance of working together to push through challenges and what could be achieved when we do so. Every project has its challenges, it is just a matter of working through them.

## Acomplishments that we're proud of

As young students, it is common for us to be overlooked and underestimated. Building this product, which is fully functional (even after our hiccups), is a huge achievement for all of us. Between building the hardware model from scratch using our resources, to designing the software, we accomplished more than we expected.

## Built with

React.js, TypeScript, Python, FastAPI, ElevenLabs API, Pinecone, OpenAI API, and Tailwind CSS

## Getting Started (Backend)

Go to the root folder of /backend/, and run:

`python -m venv ./env/`

This will create a virtual python environment.

Activate it with:

`source env/bin/activate`

Now install all pip requirements:
`pip install -r "requirements.txt"`

Now run the server with:
`python main.py`

Make sure to have a `.env` file with 
- `OPENAI_API_KEY`
- `XI_API_KEY`
- `PINECONE_API_KEY`

All initialized in the root backend folder

## Getting Started Frontend

Go to the root folder of /frontend/, and run 

`npm install`

`npm run dev`
