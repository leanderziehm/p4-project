#include <core.p4>
#include <v1model.p4>
header ethernet_t{
    bit<48> dstMac;
    bit<48> srcMac;
    bit<16> etherTypeOrLength;
}

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
    ethernet_t ethernet;
    ipv4_t ipv4;
}

// header meta{
struct meta_s{ // will it give compile error if not there?
    // ???
}

parser MyParser(packet_in packet, out headers_s headers, inout meta_s meta, inout standard_metadata_t standard_metadata){

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
        packet.extract(headers.ethernet);//what if its not valid??
        log_msg("dst={} src={} etherTypeOrLength={}",{headers.ethernet.dstMac, headers.ethernet.srcMac,headers.ethernet.etherTypeOrLength});
        transition select(headers.ethernet.etherTypeOrLength){
            // codes from https://en.wikipedia.org/wiki/EtherType
            0x0800:parse_ipv4;//add semicolon no ,
            default: accept; 
        }// implicitly reject all other states.
 }
   
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

control MyVerifyChecksum(inout headers_s headers, inout meta_s meta ){
    apply {}
}

control MyIngress(inout headers_s hdr, inout meta_s meta, inout standard_metadata_t standard_metadata){
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
    
    table ipv4_lpm{
        key = {
            hdr.ipv4.dstAddr: lpm;
            // headers.ipv4.dstIp:lpm; // longest prefix match https://en.wikipedia.org/wiki/Longest_prefix_match //lms//longest matching sequence
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
