# Final networking project
We chose to implement the "multi-stream" capability.
In fact, the implementation includes transferring several files from the server to the client according to the client's request.
Each file will be associated with a unique stream whose function will be to read from the file on the server side, and write to the file on the client side.
Each of the streams will enter a frame that we send over the connection.
This frame will enter the socket of the QUIC protocol, and it will be sent to the client.
For each stream, a number between 1000 and 2000 will be randomly drawn - and it will determine the size of the streams that pass
in bytes (this time) until the end of the connection between the server and the client.
Our multi-stream implementation was carried out using several threads.
