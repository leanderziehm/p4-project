#include <core.p4>
#include <v1model.p4>
// Controll Plane, Data Plane.

//////// HEADERS

// typedef can be used to make own named types 

// https://en.wikipedia.org/wiki/Ethernet_frame#Structure
header ethernet_t{
    bit<48> dstMac;
    bit<48> srcMac;
    //bit<32> vlantag;
    bit<16> etherTypeOrLength;
}

// https://en.wikipedia.org/wiki/IPv4#Header
header ipv4_t {
    bit<4> version; 
    bit<4> internetHeaderLengthIHL; 
    bit<6> dscpDiffserfQoS; //give different prio CS0 CS7 AF EF  https://www.iana.org/assignments/dscp-registry/dscp-registry.xhtml
    bit<2> ecnExplicitCongestionNotificationQoS; // slower sending
    bit<16> totalLenght;
    bit<16> fragID;
    bit<3> flags;//1: unused, 1: dont fragment, 1: more fragments coming,
    bit<13> fragmentOffset;
    bit<8> ttl;
    bit<8> protocol;
    bit<16> headerChecksum;
    bit<32> srcadress;
    bit<32> dstadress;
    // bit<32> options; 0 - 320 in chunks of 32
}

// a header can only contain primitive types like bit, what else?
// struct is a collection of headers. 
struct headers{
// header headers_t{
// struct headers_t{
    ethernet_t ethernet;
    ipv4_t ipv4;
}

header meta{
// struct meta{ // will it give compile error if not there?
    // ???
}

//////// PARSER
                // out headers hdr,
                // inout metadata meta,
                // inout standard_metadata_t standard_metadata) {

// parser https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-parser-states
// standard_metadata_t  https://github.com/p4lang/behavioral-model/blob/main/docs/simple_switch.md
parser MyParser(packet_in packet, out headers headers, inout meta meta, inout standard_metadata_t std_meta){



//state https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-p4-language-evolution--comparison-to-previous-versions-p4-v10v11 parser, state, control, and package.
// start state is always named start and type state
// parser state can be with next transition one of: state, accept, reject 

//transition https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-transition
    state start{
        // transiton accept;
        transition accept;
    }
}


// main
V1Switch(
MyParser()
)main;

// ; semicolons are important

// main(){
    
// }


//headers DONE

//#parser

//ingres

//#pipe

//egress

//#deparser


