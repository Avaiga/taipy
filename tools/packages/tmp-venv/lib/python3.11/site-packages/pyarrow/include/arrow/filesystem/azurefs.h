// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

#pragma once

#include <memory>
#include <string>
#include <vector>

#include "arrow/filesystem/filesystem.h"
#include "arrow/util/macros.h"
#include "arrow/util/uri.h"

namespace Azure {
namespace Core {
namespace Credentials {

class TokenCredential;

}  // namespace Credentials
}  // namespace Core
namespace Storage {

class StorageSharedKeyCredential;

}  // namespace Storage
}  // namespace Azure

namespace arrow {
namespace fs {

enum class AzureCredentialsKind : int8_t {
  /// Anonymous access (no credentials used), public
  Anonymous,
  /// Use explicitly-provided access key pair
  StorageCredentials,
  /// Use ServicePrincipleCredentials
  ServicePrincipleCredentials,
  /// Use Sas Token to authenticate
  Sas,
  /// Use Connection String
  ConnectionString
};

enum class AzureBackend : bool {
  /// Official Azure Remote Backend
  Azure,
  /// Local Simulated Storage
  Azurite
};

/// Options for the AzureFileSystem implementation.
struct ARROW_EXPORT AzureOptions {
  std::string account_dfs_url;
  std::string account_blob_url;
  AzureBackend backend = AzureBackend::Azure;
  AzureCredentialsKind credentials_kind = AzureCredentialsKind::Anonymous;

  std::string sas_token;
  std::string connection_string;
  std::shared_ptr<Azure::Storage::StorageSharedKeyCredential>
      storage_credentials_provider;
  std::shared_ptr<Azure::Core::Credentials::TokenCredential>
      service_principle_credentials_provider;

  AzureOptions();

  bool Equals(const AzureOptions& other) const;
};

/// \brief Azure-backed FileSystem implementation for ABFS and ADLS.
///
/// ABFS (Azure Blob Storage - https://azure.microsoft.com/en-us/products/storage/blobs/)
/// object-based cloud storage system.
///
/// ADLS (Azure Data Lake Storage -
/// https://azure.microsoft.com/en-us/products/storage/data-lake-storage/)
/// is a scalable data storage system designed for big-data applications.
/// ADLS provides filesystem semantics, file-level security, and Hadoop
/// compatibility. Gen1 exists as a separate object that will retired
/// on Feb 29, 2024. New ADLS accounts will use Gen2 instead, which is
/// implemented on top of ABFS.
///
/// TODO: GH-18014 Complete the internal implementation
/// and review the documentation
class ARROW_EXPORT AzureFileSystem : public FileSystem {
 public:
  ~AzureFileSystem() override = default;

  std::string type_name() const override { return "abfs"; }

  /// Return the original Azure options when constructing the filesystem
  const AzureOptions& options() const;

  bool Equals(const FileSystem& other) const override;

  Result<FileInfo> GetFileInfo(const std::string& path) override;

  Result<FileInfoVector> GetFileInfo(const FileSelector& select) override;

  Status CreateDir(const std::string& path, bool recursive = true) override;

  Status DeleteDir(const std::string& path) override;

  Status DeleteDirContents(const std::string& path, bool missing_dir_ok = false) override;

  Status DeleteRootDirContents() override;

  Status DeleteFile(const std::string& path) override;

  Status Move(const std::string& src, const std::string& dest) override;

  Status CopyFile(const std::string& src, const std::string& dest) override;

  Result<std::shared_ptr<io::InputStream>> OpenInputStream(
      const std::string& path) override;

  Result<std::shared_ptr<io::InputStream>> OpenInputStream(const FileInfo& info) override;

  Result<std::shared_ptr<io::RandomAccessFile>> OpenInputFile(
      const std::string& path) override;

  Result<std::shared_ptr<io::RandomAccessFile>> OpenInputFile(
      const FileInfo& info) override;

  Result<std::shared_ptr<io::OutputStream>> OpenOutputStream(
      const std::string& path,
      const std::shared_ptr<const KeyValueMetadata>& metadata = {}) override;

  Result<std::shared_ptr<io::OutputStream>> OpenAppendStream(
      const std::string& path,
      const std::shared_ptr<const KeyValueMetadata>& metadata = {}) override;

  static Result<std::shared_ptr<AzureFileSystem>> Make(
      const AzureOptions& options, const io::IOContext& = io::default_io_context());

 private:
  explicit AzureFileSystem(const AzureOptions& options, const io::IOContext& io_context);

  class Impl;
  std::unique_ptr<Impl> impl_;
};

}  // namespace fs
}  // namespace arrow
