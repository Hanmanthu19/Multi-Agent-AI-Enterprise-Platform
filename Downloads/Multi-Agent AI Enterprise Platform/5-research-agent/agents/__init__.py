def __init__(self):
        self.upload_dir = os.path.join("data", "uploads")
        
        # If 'data/uploads' exists as a file instead of a folder, delete the file first
        if os.path.isfile(self.upload_dir):
            os.remove(self.upload_dir)

        os.makedirs(self.upload_dir, exist_ok=True)
        self.vectorstore = None
        self.structured_dfs = {}
        self.raw_documents = []
        self.reload_company_datasets()