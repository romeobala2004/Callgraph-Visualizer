void init_server() {
    create_socket();
    bind_port();
}
 
void accept_loop() {
    handle_client();
}
 
void handle_client() {
    parse_request();
    send_response();
}
