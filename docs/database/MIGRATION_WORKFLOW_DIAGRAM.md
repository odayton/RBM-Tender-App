# Database Migration Workflow - Visual Guide

This document provides visual representations of the migration workflow.

---

## 📊 Complete Migration Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     MIGRATION WORKFLOW                          │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │  Make Model      │
                    │  Changes         │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Create          │
                    │  Migration       │
                    │  (flask migrate) │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Review          │
                    │  Generated       │
                    │  Migration File  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Run Validation  │
                    │  Checker         │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │                  │
                    ▼                  ▼
            ┌──────────────┐   ┌──────────────┐
            │   ERRORS?    │   │  WARNINGS?   │
            └──────┬───────┘   └──────┬───────┘
                   │                  │
              YES  │                  │  Review
                   ▼                  ▼
            ┌──────────────┐   ┌──────────────┐
            │  Fix Issues  │   │ Address or   │
            │  in File     │   │ Document     │
            └──────┬───────┘   └──────┬───────┘
                   │                  │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Create Local    │
                   │  Backup          │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Test Upgrade    │
                   │  Locally         │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Test            │
                   │  Application     │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Test Rollback   │
                   │  (Downgrade)     │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Test Upgrade    │
                   │  Again           │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Commit to Git   │
                   │  (Hook Runs)     │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Push & Create   │
                   │  Pull Request    │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Code Review     │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Merge to Main   │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  PRODUCTION      │
                   │  DEPLOYMENT      │
                   │  (See below)     │
                   └──────────────────┘
```

---

## 🚀 Production Deployment Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│               PRODUCTION DEPLOYMENT WORKFLOW                    │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │  SSH to          │
                    │  Production      │
                    │  Server          │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Pull Latest     │
                    │  Code from Git   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Create          │
                    │  Database        │
                    │  Backup          │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Verify Backup   │
                    │  Was Created     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Check           │
                    │  Migration       │
                    │  Status          │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Validate        │
                    │  Migrations      │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │                  │
                    ▼                  ▼
            ┌──────────────┐   ┌──────────────┐
            │  Issues?     │   │  All Clear?  │
            └──────┬───────┘   └──────┬───────┘
                   │                  │
              YES  │                  │  NO
                   ▼                  ▼
            ┌──────────────┐   ┌──────────────┐
            │  STOP!       │   │  Run         │
            │  Investigate │   │  Migration   │
            │  & Fix       │   │  Upgrade     │
            └──────────────┘   └──────┬───────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │  Watch       │
                              │  Output for  │
                              │  Errors      │
                              └──────┬───────┘
                                     │
                            ┌────────┴─────────┐
                            │                  │
                     ERROR  ▼                  ▼  SUCCESS
                    ┌──────────────┐   ┌──────────────┐
                    │  Attempt     │   │  Restart     │
                    │  Rollback or │   │  Application │
                    │  Restore     │   │  Service     │
                    └──────┬───────┘   └──────┬───────┘
                           │                  │
                           ▼                  ▼
                    ┌──────────────┐   ┌──────────────┐
                    │  Notify Team │   │  Verify      │
                    │  Document    │   │  Status      │
                    │  Issue       │   └──────┬───────┘
                    └──────────────┘          │
                                              ▼
                                     ┌──────────────┐
                                     │  Test        │
                                     │  Critical    │
                                     │  Features    │
                                     └──────┬───────┘
                                            │
                                            ▼
                                     ┌──────────────┐
                                     │  Monitor     │
                                     │  for 15-30   │
                                     │  Minutes     │
                                     └──────┬───────┘
                                            │
                                            ▼
                                     ┌──────────────┐
                                     │  DEPLOYMENT  │
                                     │  COMPLETE    │
                                     └──────────────┘
```

---

## 🛡️ Safety Checkpoints

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAFETY CHECKPOINTS                           │
└─────────────────────────────────────────────────────────────────┘

Checkpoint 1: Creation
├─ Review auto-generated migration
├─ Check upgrade() and downgrade()
└─ Verify expected changes

Checkpoint 2: Validation
├─ Run migration checker
├─ Check for errors
└─ Review warnings

Checkpoint 3: Local Testing
├─ Create backup
├─ Test upgrade
├─ Test application
├─ Test rollback
└─ Test upgrade again

Checkpoint 4: Code Review
├─ Another developer reviews
├─ Check for data loss risks
└─ Verify rollback plan

Checkpoint 5: Pre-Production
├─ Test on production clone
└─ Verify with production data

Checkpoint 6: Production Backup
├─ Create backup
├─ Verify backup exists
└─ Note backup filename

Checkpoint 7: Deployment
├─ Validate before running
├─ Monitor during migration
└─ Verify after completion

Checkpoint 8: Post-Deployment
├─ Test critical features
├─ Check error logs
└─ Monitor for 30 minutes
```

---

## 🔄 Decision Tree - When Things Go Wrong

```
┌─────────────────────────────────────────────────────────────────┐
│              MIGRATION FAILURE DECISION TREE                    │
└─────────────────────────────────────────────────────────────────┘

                 Migration Failed?
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
    In Production?              In Development?
          │                           │
    ┌─────┴─────┐               ┌─────┴─────┐
    │           │               │           │
    ▼           ▼               ▼           ▼
Complete?   Partial?        Can Fix?    Can't Fix?
    │           │               │           │
    │           │               │           │
    ▼           ▼               ▼           ▼
Try         Restore      Fix &        Reset
Rollback    Backup       Retest       Database
    │           │               │           │
    │           │               └───────────┘
    │           │                     │
    └───────┬───┘                     │
            │                         │
            ▼                         ▼
    Worked?                     Continue
        │                       Development
    ┌───┴───┐
    │       │
   YES     NO
    │       │
    ▼       ▼
 Good!   Restore
         Backup
```

---

## 📝 Quick Decision Guide

### Should I create a new migration or modify existing?

```
                 ┌──────────────────┐
                 │ Has migration    │
                 │ been deployed to │
                 │ production?      │
                 └────────┬─────────┘
                          │
           ┌──────────────┴──────────────┐
           │                             │
          YES                           NO
           │                             │
           ▼                             ▼
    ┌──────────────┐            ┌──────────────┐
    │ Create NEW   │            │ Has it been  │
    │ migration    │            │ committed to │
    │ to modify    │            │ Git?         │
    └──────────────┘            └──────┬───────┘
                                       │
                        ┌──────────────┴──────────────┐
                        │                             │
                       YES                           NO
                        │                             │
                        ▼                             ▼
                 ┌──────────────┐            ┌──────────────┐
                 │ Create NEW   │            │ OK to modify │
                 │ migration    │            │ existing     │
                 └──────────────┘            └──────────────┘
```

### Should I rollback or restore?

```
                 ┌──────────────────┐
                 │ Can database     │
                 │ still connect?   │
                 └────────┬─────────┘
                          │
           ┌──────────────┴──────────────┐
           │                             │
          YES                           NO
           │                             │
           ▼                             ▼
    ┌──────────────┐            ┌──────────────┐
    │ Try          │            │ RESTORE from │
    │ ROLLBACK     │            │ backup       │
    └──────┬───────┘            └──────────────┘
           │
           ▼
    ┌──────────────┐
    │ Did rollback │
    │ succeed?     │
    └──────┬───────┘
           │
    ┌──────┴──────┐
    │             │
   YES           NO
    │             │
    ▼             ▼
 Good!     ┌──────────────┐
           │ RESTORE from │
           │ backup       │
           └──────────────┘
```

---

## 🎯 Key Stages Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIGRATION LIFECYCLE                          │
└─────────────────────────────────────────────────────────────────┘

1. CREATION              → Model changes + flask migrate create
                           ↓
2. VALIDATION            → Review file + run checker
                           ↓
3. LOCAL TESTING         → Upgrade + Test + Rollback
                           ↓
4. VERSION CONTROL       → Commit + Push + Review
                           ↓
5. PRE-PRODUCTION        → Test with production data
                           ↓
6. PRODUCTION BACKUP     → Create and verify backup
                           ↓
7. DEPLOYMENT            → Apply migration + Restart
                           ↓
8. VERIFICATION          → Test + Monitor + Document
                           ↓
9. MAINTENANCE           → Monitor logs + User feedback

Each stage has:
├─ Required actions
├─ Safety checks
├─ Success criteria
└─ Rollback plan
```

---

## 📊 Migration File Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                  MIGRATION FILE STATES                          │
└─────────────────────────────────────────────────────────────────┘

    CREATED                  │  Migration file created
       ↓                     │  in migrations/versions/
    REVIEWED                 │  Developer reviews code
       ↓                     │  Checks upgrade/downgrade
    VALIDATED                │  Passes validation checks
       ↓                     │  No errors or warnings
    TESTED                   │  Tested locally
       ↓                     │  Upgrade and rollback work
    COMMITTED                │  Added to version control
       ↓                     │  Pre-commit hook passed
    REVIEWED (CODE)          │  Peer reviewed
       ↓                     │  Approved for merge
    MERGED                   │  In main branch
       ↓                     │  Ready for deployment
    PRE-PROD TESTED          │  Tested with prod data
       ↓                     │  No issues found
    DEPLOYED (PROD)          │  Applied to production
       ↓                     │  Application restarted
    VERIFIED                 │  Monitoring complete
       ↓                     │  No issues detected
    STABLE                   │  In production > 24hrs
                            │  No rollback needed
```

---

## 🚨 Emergency Rollback Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   EMERGENCY ROLLBACK                            │
└─────────────────────────────────────────────────────────────────┘

          PRODUCTION ISSUE DETECTED
                    │
                    ▼
          ┌──────────────────┐
          │ Stop application │
          │ if critically    │
          │ broken           │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Document error   │
          │ Save logs        │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Attempt:         │
          │ flask migrate    │
          │ rollback         │
          └────────┬─────────┘
                   │
          ┌────────┴─────────┐
          │                  │
       SUCCESS            FAILURE
          │                  │
          ▼                  ▼
   ┌──────────────┐   ┌──────────────┐
   │ Restart      │   │ Restore from │
   │ application  │   │ backup       │
   └──────┬───────┘   └──────┬───────┘
          │                  │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Verify           │
          │ application      │
          │ works            │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Notify team      │
          │ Document issue   │
          │ Plan fix         │
          └──────────────────┘

Time Target: < 15 minutes from detection to recovery
```

---

## 📚 Related Documentation

- **[Database Migration Workflow](DATABASE_MIGRATION_WORKFLOW.md)** - Complete guide
- **[Migration Checklist](MIGRATION_CHECKLIST.md)** - Quick reference
- **[Tools README](../scripts/development/MIGRATION_TOOLS_README.md)** - Development tools

---

**Remember**: The goal is safe, predictable database changes with clear rollback capability at every stage!

