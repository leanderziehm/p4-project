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
    bit<6> dscpDiffserfQoS; 
    bit<2> ecnExplicitCongestionNotificationQoS; 
    bit<16> totalLenght;
    bit<16> fragmentID;
    bit<3> flags;
    bit<13> fragmentOffset;
    bit<8> ttl;
    bit<8> protocol;
    bit<16> headerChecksum;
    bit<32> srcIp;
    bit<32> dstAddr;
}
struct headers_s{
    ethernet_t ethernet;
    ipv4_t ipv4;
}

struct meta_s{ 
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
        log_msg("ipv4");
        packet.extract(headers.ipv4);
        transition accept;
    }
}

control MyVerifyChecksum(inout headers_s headers, inout meta_s meta ){
    apply {}
}

control MyIngress(inout headers_s hdr, inout meta_s meta, inout standard_metadata_t standard_metadata){
    action drop(){
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(bit<48> newMac,bit<9> ethernetEgressPort){
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        hdr.ethernet.srcMac = hdr.ethernet.dstMac; //whats the point of setting this? for path traversal?
        hdr.ethernet.dstMac = newMac;
        log_msg("ttl={}",{hdr.ipv4.ttl});
        standard_metadata.egress_spec = ethernetEgressPort;
    }

    table ipv4_lpm{
        key = {
            hdr.ipv4.dstAddr: lpm;
        }

        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        default_action = drop; 
    }

    apply{
        if (hdr.ipv4.isValid()){ 
            ipv4_lpm.apply();
        }
    }
}

control MyEgress(inout headers_s headers, inout meta_s meta, inout standard_metadata_t standard_m ){
    apply{}
}

control MyComputeChecksum(inout headers_s headers, inout meta_s meta){
    apply{

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
              headers.ipv4.dstAddr },
            headers.ipv4.headerChecksum,
            HashAlgorithm.csum16);
    }
}

control MyDeparser(packet_out packet, in headers_s headers){
    apply{
        packet.emit(headers.ethernet);
        packet.emit(headers.ipv4);
    }
}

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
)main;
