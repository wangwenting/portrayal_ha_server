namespace java com.bfd.probuf_thrift
namespace py portrayal_server.interface.portrayal

struct ErrMsg {
    1: i32 code,
    2: string descirbe
}

struct Result {
    1: i32 status,
    2: binary value,
    3: string modules_path,
    4: ErrMsg msg
}

service PortrayalService{
string analyze_json(1:string request, 2:string modules),

Result analyze_protobuf(1:string request, 2:string modules),
}
