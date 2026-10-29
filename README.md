# Care Workflow Simulator

A local, dependency-free demo of a care check-in workflow. It shows a mock check-in, scripted responses, review alert creation, acknowledgement, and reset. Cases are synthetic and kept in memory only.

## Run locally

With Python 3.12 or newer, run `python3 app.py` and open the loopback address printed by the program. Run `python3 -m unittest discover -s tests -v` to check the domain rules and HTTP boundary.

## Safety and scope

The server binds only to `127.0.0.1`. There are no phone numbers, real patients, external services, database files, credentials, outbound messages, or clinical advice. The interface only offers scripted replies, and reset discards all demo state. This is a workflow demonstration, not a medical system. Any real-world adaptation would require a separate privacy, authentication, clinical safety, and operational review.
