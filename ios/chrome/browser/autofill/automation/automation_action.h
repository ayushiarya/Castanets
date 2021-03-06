// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef IOS_CHROME_BROWSER_AUTOFILL_AUTOMATION_AUTOMATION_ACTION_H_
#define IOS_CHROME_BROWSER_AUTOFILL_AUTOMATION_AUTOMATION_ACTION_H_

#import <Foundation/Foundation.h>
#include "base/values.h"

// AutomationAction consumes description of actions in base::Value format,
// generated in json by an extension and executes them on the current
// active web page. AutomationAction is an abstract superclass for a class
// cluster, the class method -actionWithValueDictionary: returns concrete
// subclasses for the various possible actions.
@interface AutomationAction : NSObject

// Returns an concrete instance of a subclass of AutomationAction.
+ (instancetype)actionWithValueDictionary:
                    (const base::DictionaryValue&)actionDictionary
                                    error:(NSError**)error;

// Prevents creating rogue instances, the init methods are private.
- (instancetype)init NS_UNAVAILABLE;

// For subclasses to implement, execute the action.
- (NSError*)execute WARN_UNUSED_RESULT;
@end

#endif  // IOS_CHROME_BROWSER_AUTOFILL_AUTOMATION_AUTOMATION_ACTION_H_
