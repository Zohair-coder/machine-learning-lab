/**
 * ML Lab Service
 * Functionality to create and manage Lab projects, services, datasets, models, and experiments.
 *
 * OpenAPI spec version: 0.2.0-SNAPSHOT
 *
 *
 * NOTE: This class is auto generated by the swagger code generator program.
 * https://github.com/swagger-api/swagger-codegen.git
 * Do not edit the class manually.
 *
 */

import ApiClient from '../ApiClient';

/**
 * The GitInfo model module.
 * @module model/GitInfo
 * @version 0.2.0-SNAPSHOT
 */
export default class GitInfo {
  /**
   * Constructs a new <code>GitInfo</code>.
   * @alias module:model/GitInfo
   * @class
   */

  constructor() {}

  /**
   * Constructs a <code>GitInfo</code> from a plain JavaScript object, optionally creating a new instance.
   * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
   * @param {Object} data The plain JavaScript object bearing properties of interest.
   * @param {module:model/GitInfo} obj Optional instance to populate.
   * @return {module:model/GitInfo} The populated <code>GitInfo</code> instance.
   */
  static constructFromObject(data, obj) {
    if (data) {
      obj = obj || new GitInfo();

      if (data.hasOwnProperty('commit')) {
        obj['commit'] = ApiClient.convertToType(data['commit'], 'String');
      }
      if (data.hasOwnProperty('remoteUrl')) {
        obj['remoteUrl'] = ApiClient.convertToType(data['remoteUrl'], 'String');
      }
      if (data.hasOwnProperty('branch')) {
        obj['branch'] = ApiClient.convertToType(data['branch'], 'String');
      }
      if (data.hasOwnProperty('userName')) {
        obj['userName'] = ApiClient.convertToType(data['userName'], 'String');
      }
      if (data.hasOwnProperty('userEmail')) {
        obj['userEmail'] = ApiClient.convertToType(data['userEmail'], 'String');
      }
    }
    return obj;
  }

  /**
   * @member {String} commit
   */
  commit = undefined;
  /**
   * @member {String} remoteUrl
   */
  remoteUrl = undefined;
  /**
   * @member {String} branch
   */
  branch = undefined;
  /**
   * @member {String} userName
   */
  userName = undefined;
  /**
   * @member {String} userEmail
   */
  userEmail = undefined;
}
