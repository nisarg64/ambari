/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

var App = require('app');
var credentialsUtils = require('utils/credentials');

App.ManageCredentialsFormView = Em.View.extend({
  templateName: require('templates/common/form/manage_credentilas_form'),
  viewName: 'manageCredentialsForm',
  principal: "",
  password: "",

  /**
   * Store Admin credentials checkbox value
   *
   * @type {boolean}
   */
  storeCredentials: false,

  /**
   * Status of persistent storage. Returns <code>true</code> if persistent storage is available.
   * @type {boolean}
   */
  storePersisted: false,

  /**
   * Disable checkbox if persistent storage not available
   *
   * @type {boolean}
   */
  checkboxDisabled: Ember.computed.not('storePersisted'),

  /**
   * Credentials can be removed, in case when they stored to persistent secure storage.
   *
   * @type {boolean}
   */
  isRemovable: false,

  /**
   * Remove button disabled status.
   *
   * @type {boolean}
   */
  isRemoveDisabled: true,

  /**
   * Signalize that action was performed and waiting for result.
   *
   * @type {boolean}
   */
  isActionInProgress: false,

  /**
   * Status message of performed action, e.g. remove or save credentials. Set to <code>false</code> to hide this message.
   *
   * @type {boolean|string}
   */
  actionStatus: false,

  isSubmitDisabled: function() {
    return Em.isEmpty(this.get('principal')) || Em.isEmpty(this.get('password'));
  }.property('principal', 'password'),

  /**
   * Returns storage type used to save credentials e.g. <b>persistent</b>, <b>temporary</b> (default)
   *
   * @type {string}
   */
  storageType: function() {
    return this.get('storeCredentials') ? credentialsUtils.STORE_TYPES.PERSISTENT : credentialsUtils.STORE_TYPES.TEMPORARY;
  }.property('storeCredentials'),

  /**
   * Message to display in tooltip regarding persistent storage state.
   *
   * @type {string}
   */
  hintMessage: function() {
    return this.get('storePersisted') ?
      Em.I18n.t('admin.kerberos.credentials.store.hint.supported') :
      Em.I18n.t('admin.kerberos.credentials.store.hint.not.supported');
  }.property('storePersisted'),

  /**
   * Observe changes for principal and password.
   * Hide status message and toggle action progress if performed.
   */
  formInputObserver: function() {
    if (this.get('actionStatus') || this.get('isActionInProgress')) {
      this.setInProgress(false);
      this.set('actionStatus', false);
    }
  }.observes('password', 'principal'),

  didInsertElement: function() {
    this._super();
    App.tooltip(this.$('[rel="tooltip"]'));
  },

  willInsertElement: function() {
    this._super();
    this.prepareContent();
  },

  prepareContent: function() {
    var self = this;
    credentialsUtils.isStorePersisted(App.get('clusterName')).then(function(isPersisted) {
      Em.run.next(function() {
        self.set('storePersisted', isPersisted);
      });
    });
    credentialsUtils.credentials(App.get('clusterName'), function(credentials) {
      Em.run.next(function() {
        self.set('isRemovable', credentialsUtils.isKDCCredentialsPersisted(credentials));
        self.set('isRemoveDisabled', !self.get('isRemovable'));
      });
    });
  },

  /**
   * Save credentials action.
   *
   * @returns {boolean|$.Deferred}
   */
  saveKDCCredentials: function () {
    var self = this;
    var dfd = $.Deferred();

    this.setInProgress(true);
    credentialsUtils.createOrUpdateCredentials(
      App.get('clusterName'),
      credentialsUtils.ALIAS.KDC_CREDENTIALS,
      credentialsUtils.createCredentialResource(this.get('principal'), this.get('password'), this.get('storageType')))
      .always(function() {
        self.setInProgress(false);
        self.prepareContent();
        self.set('actionStatus', Em.I18n.t('common.success'));
        self.get('parentView').set('isCredentialsSaved', true);
        dfd.resolve();
      });
    return dfd.promise();
  },

  /**
   * Remove KDC credentials action.
   *
   * @returns {App.ModalPopup}
   */
  removeKDCCredentials: function() {
    var t = Em.I18n.t;
    var self = this;
    this.set('actionStatus', false);
    var popup = App.showConfirmationPopup(
      function() {
        self.setInProgress(true);
        credentialsUtils.removeCredentials(App.get('clusterName'), credentialsUtils.ALIAS.KDC_CREDENTIALS)
          .always(function() {
            self.setInProgress(false);
            self.prepareContent();
            self.set('actionStatus', Em.I18n.t('common.success'));
            self.get('parentView').set('isCredentialsRemoved', true);
          });
      }, t('admin.kerberos.credentials.remove.confirmation.body'),
      function () {},
      null,
      t('yes'),
      false);
    popup.set('secondary', t('no'));
    return popup;
  },

  /**
   * Toggle action status and disable/enable appropriate buttons.
   *
   * @param {boolean} [isInProgress=false] progress status
   */
  setInProgress: function(isInProgress) {
    if (isInProgress) {
      this.set('actionStatus', false);
      if (this.get('isRemovable')) {
        this.set('isRemoveDisabled', true);
      }
      this.set('isSubmitDisabled', true);
      this.set('isActionInProgress', true);
    } else {
      if (this.get('isRemovable')) {
        this.set('isRemoveDisabled', false);
      }
      this.set('isSubmitDisabled', false);
      this.set('isActionInProgress', false);
    }
  }
});