from party3rd.c_plus_clients import AclVersionCollector


class MemoryStoreCollector(AclVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "memorystore"
