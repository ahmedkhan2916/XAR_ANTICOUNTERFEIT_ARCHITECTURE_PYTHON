import hmac
import hashlib
from typing import List, Dict



class SignatureEngine:
    print("Signature Engine Initialized")
    """ 
       Responsible for:
     - Generating secure signature
     - Verifying integrity of data + pattern + context
     - Ensuring tamper-proofing
     """
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()  # Store as bytes for HMAC

    def build_message(self,binary_data:str,pattern_hash:str,context:str) -> str:
        """Construct a unique message for signing based on all inputs.
           Standardize message format (VERY IMPORTANT).
        """
        return f"{binary_data}|{pattern_hash}|{context}"
    
    def generate_signature(self, binary_data:str,pattern_hash:str,context:str)->str:
        message=self.build_message(binary_data,pattern_hash,context).encode()

        signature=hmac.new(self.secret_key,message,hashlib.sha256).hexdigest()

        return signature
    
    def verify_signature(self,binary_data:str,pattern_hash:str,context:str,signature:str)->bool:
        expected_signature=self.generate_signature(binary_data,pattern_hash,context)

        return hmac.compare_digest(expected_signature,signature)