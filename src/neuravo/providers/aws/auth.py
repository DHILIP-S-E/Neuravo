"""AWS credential resolution for Neuravo providers.

Reserved for shared AWS authentication logic (credential chain resolution,
STS role assumption, SSO) used by Bedrock and any future AWS-backed
provider. Not yet implemented — v0.1's ``BedrockProvider.initialize``
currently owns credential handling directly; this module is the intended
home once that logic needs to be shared across more than one AWS provider.
"""
