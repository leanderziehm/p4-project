#include <core.p4>
#include <v1model.p4>
// Controll Plane, Data Plane.

// enum bit<16> EtherType {
//   VLAN      = 0x8100,
//   IPV4      = 0x0800,
//   IPV6      = 0x86dd
// }

//////// HEADERS

// typedef can be used to make own named types 

// variable types https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-base-types
// baseType
//     : BOOL
//     | ERROR
//     | BIT
//     | INT
//     | STRING
//     | BIT '<' INTEGER '>'
//     | INT '<' INTEGER '>'
//     | VARBIT '<' INTEGER '>'
//     | BIT '<' '(' expression ')' '>'
//     | INT '<' '(' expression ')' '>'
//     | VARBIT '<' '(' expression ')' '>'
//     ;
// https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-derived-types
// enum
// header
// header stacks
// struct
// header_union
// tuple
// type specialization
// extern
// parser
// control
// package


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
    bit<16> fragmentID;
    bit<3> flags;//1: unused, 1: dont fragment, 1: more fragments coming,
    bit<13> fragmentOffset;
    bit<8> ttl;
    bit<8> protocol;
    bit<16> headerChecksum;
    bit<32> srcIp;
    bit<32> dstIp;
    // bit<32> options; 0 - 320 in chunks of 32
}

// a header can only contain primitive types like bit, what else?
// struct is a collection of headers. 
struct headers_s{
// header headers_t{
// struct headers_t{
    ethernet_t ethernet;
    ipv4_t ipv4;
}

// header meta{
struct meta_s{ // will it give compile error if not there?
    // ???
}

//////// PARSER
                // out headers hdr,
                // inout metadata meta,
                // inout standard_metadata_t standard_metadata) {

// parser https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-parser-states
// standard_metadata_t  https://github.com/p4lang/behavioral-model/blob/main/docs/simple_switch.md
parser MyParser(packet_in packet, out headers_s headers, inout meta_s meta, inout standard_metadata_t standard_metadata){
// parser state can be with next transition one of: state, accept, reject 
//state https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-p4-language-evolution--comparison-to-previous-versions-p4-v10v11 parser, state, control, and package.
// start state is always named start and type state
//transition https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-transition
//always end with accept or reject or new state.

    // state start {
        // b.extract(p.ethernet);
        // transition select(p.ethernet.etherType) {
            // 0x0800: parse_ipv4;
            // no default rule: all other packets rejected
        // }
    // }

     state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(headers.ethernet);
        transition select(headers.ethernet.etherTypeOrLength) {
            0x0800: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(headers.ipv4);
        transition accept;
    }



    state start2{
        // log_msg("hello"); //https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4
        // if is not allowed in here
        packet.extract(headers.ethernet);//what if its not valid??
        log_msg("dst={} src={} etherTypeOrLength={}",{headers.ethernet.dstMac, headers.ethernet.srcMac,headers.ethernet.etherTypeOrLength});
        transition select(headers.ethernet.etherTypeOrLength){
            // codes from https://en.wikipedia.org/wiki/EtherType
            0x0800:parse_ipv4;//add semicolon no ,
            // 0x0806:parse_arp;
            // 0x86DD:parse_ipv6;
            // 0x8100:parse_vlanTag;
            // default: reject; // EXPLICIT REJECT FOR SOME REASON NOT ALLOWED IN BMV2
            default: accept; 
            
        }// implicitly reject all other states.
        // transition accept;
 }
        // if (headers.ethernet.isValid()){
        //  transition parse_mac;
        //  }
        //  else{
            // drop();
            //reject();
        //  }
        // if(packet.headers)
   
    state parse_ipv42 {
        log_msg("ipv4");
        packet.extract(headers.ipv4);
        transition accept;
    }
    state parse_arp {
        log_msg("arp");
        transition reject;// EXPLICIT REJECT FOR SOME REASON NOT ALLOWED IN BMV2
    }
    state parse_ipv6 {
        log_msg("ipv6");
        transition reject;// EXPLICIT REJECT FOR SOME REASON NOT ALLOWED IN BMV2
    }
     state parse_vlanTag{
        log_msg("vlanTag");
        transition reject;// EXPLICIT REJECT FOR SOME REASON NOT ALLOWED IN BMV2
     }

}

/// Verify Checksum
//control https://p4lang.github.io/p4-spec/docs/P4-16-v1.2.1.html#sec-control
// expecting ACTION or CONST or TABLE
control MyVerifyChecksum(inout headers_s headers, inout meta_s meta ){
    apply {}
}



// @pipeline
// control Ingress<H, M>(inout H hdr,
//                       inout M meta,
//                       inout standard_metadata_t standard_metadata);
// @pipeline
// control Egress<H, M>(inout H hdr,
//                      inout M meta,
//                      inout standard_metadata_t standard_metadata);


control MyIngress(inout headers_s headers, inout meta_s meta, inout standard_metadata_t standard_metadata){
    //tables and actions

    action drop(){
        mark_to_drop(standard_metadata);
    }

// "10.0.1.2/31"
    action forward_ipv4_packet(bit<48> newMac,bit<9> ethernetEgressPort){//port standard metadata????
        // https://github.com/p4lang/behavioral-model/blob/main/docs/simple_switch.md
        // headers.ipv4.ttl = 69;// headers.ipv4.ttl - 1;
        headers.ipv4.ttl = headers.ipv4.ttl - 1;
        headers.ethernet.srcMac = headers.ethernet.dstMac; //whats the point of setting this? for path traversal?
        headers.ethernet.dstMac = newMac;
        log_msg("ttl={}",{headers.ipv4.ttl});
        standard_metadata.egress_spec = ethernetEgressPort;//https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4 and https://github.com/p4lang/behavioral-model/blob/main/docs/simple_switch.md
    }

    // https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4
    
    table forward{
        key = {
            headers.ipv4.dstIp:lpm; // longest prefix match https://en.wikipedia.org/wiki/Longest_prefix_match //lms//longest matching sequence
        }//no commas here

        actions = {
            forward_ipv4_packet;// semicolons in object here
            drop;
            NoAction;//do we need this?
        }
        default_action = drop; //() or no?JJ
    }

    apply{
        // forward.apply();
        if (headers.ipv4.isValid()){ // !! impoartant check if header is valid that key depends on
            forward.apply();
        }
    }
}


control MyEgress(inout headers_s headers, inout meta_s meta, inout standard_metadata_t standard_m ){
    apply{}//? what is the difference between ingress and egress? any new features?
}


/// compute checksum
control MyComputeChecksum(inout headers_s headers, inout meta_s meta){
    apply{//}

     update_checksum(
            headers.ipv4.isValid(),
            { headers.ipv4.version,
              headers.ipv4.internetHeaderLengthIHL,
              headers.ipv4.dscpDiffserfQoS,
              headers.ipv4.ecnExplicitCongestionNotificationQoS,
              headers.ipv4.totalLenght,
              headers.ipv4.fragmentID,
              headers.ipv4.flags,
              headers.ipv4.fragmentOffset,
              headers.ipv4.ttl,
              headers.ipv4.protocol,
              headers.ipv4.srcIp,
              headers.ipv4.dstIp },
            headers.ipv4.headerChecksum,
            HashAlgorithm.csum16);

    }
}

/// deparser
control MyDeparser(packet_out packet, in headers_s headers){
    apply{
        packet.emit(headers.ethernet);
        packet.emit(headers.ipv4);

        // headers.emit(packet.ethernet);
        // if(headers.ipv4.isValid()){
            // headers.emit(packet.ipv4);
        // }
    }
}


// main
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
)main;
// ComputeChecksum()
// ; semicolons are important

// main(){
    
// }


//headers DONE

//#parser DONE
//#verify checksum
//#ingres
// pipe
//#egress
//#compute checksum
//#deparser

// code reference from: line 715 in https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4
// /*
//  * Architecture.
//  *
//  * M must be a struct.
//  *
//  * H must be a struct where every one if its members is of type
//  * header, header stack, or header_union.
//  */

// parser Parser<H, M>(packet_in b,
//                     out H parsedHdr,
//                     inout M meta,
//                     inout standard_metadata_t standard_metadata);

// /*
//  * The only legal statements in the body of the VerifyChecksum control
//  * are: block statements, calls to the verify_checksum and
//  * verify_checksum_with_payload methods, and return statements.
//  */
// control VerifyChecksum<H, M>(inout H hdr,
//                              inout M meta);
// @pipeline
// control Ingress<H, M>(inout H hdr,
//                       inout M meta,
//                       inout standard_metadata_t standard_metadata);
// @pipeline
// control Egress<H, M>(inout H hdr,
//                      inout M meta,
//                      inout standard_metadata_t standard_metadata);

// /*
//  * The only legal statements in the body of the ComputeChecksum
//  * control are: block statements, calls to the update_checksum and
//  * update_checksum_with_payload methods, and return statements.
//  */
// control ComputeChecksum<H, M>(inout H hdr,
//                               inout M meta);

// /*
//  * The only legal statements in the body of the Deparser control are:
//  * calls to the packet_out.emit() method.
//  */
// @deparser
// control Deparser<H>(packet_out b, in H hdr);

// package V1Switch<H, M>(Parser<H, M> p,
//                        VerifyChecksum<H, M> vr,
//                        Ingress<H, M> ig,
//                        Egress<H, M> eg,
//                        ComputeChecksum<H, M> ck,
//                        Deparser<H> dep
//                        );